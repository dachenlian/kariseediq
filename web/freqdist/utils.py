from collections import Counter, OrderedDict
import functools
from itertools import groupby, chain
import logging
from multiprocessing import Pool, cpu_count, Manager
from pathlib import Path
import re
from typing import Sequence, Tuple, List, Dict
from typing import OrderedDict as TypingOrderedDict

import chardet
from django.db.models import Q

from .models import TextFile
from core.models import Headword, Example, Sense

logger = logging.getLogger(__name__)

sent_boundary = ['.', '。', '!', '！', '?', '？', ';', '；']
SENT_BOUNDARY_RE = re.compile(rf'[{"".join(sent_boundary)}]')

punctuations = "".join(['，', '。', '？', '！', '：', '；', '（', '）', '「', '』',
                        ',', '.', '?', '!', ':', ';', '(', ')', '"', '“',
                        '”', '~', '/', '-'])  # 共17個
PUNCTUATION_RE = re.compile(rf'[{"".join(punctuations)}]')


def _has_content(s):
    if not s:
        return False
    elif s.isspace():
        return False
    elif s == 'NULL':
        return False
    return True


def _split_by_word_boundary(text):
    return list(filter(_has_content, text.split()))


def _split_by_sent_boundary(text: str):
    r = list(filter(_has_content, (t.strip() for t in SENT_BOUNDARY_RE.split(text))))
    # with open('test_dict_sent_split.txt', 'a') as f:
    #     for s in r:
    #         print(s, file=f)
    return r


# def _get_word_details_multiproc(word_freq_items: Sequence, senses: list):
#     max_workers = cpu_count() // 4*3 + (cpu_count() % 4*3 > 0)
#     with Pool(max_workers=max_workers) as pool:


# def _compile_attr_groups(word_details: List[dict], attr: str) -> TypingOrderedDict:
#     sorting_key = {
#         'word_class': Sense.WordClassChoices,
#         'focus': Sense.FocusChoices
#     }
#     logger.debug(f'Compiling {attr}')
#     word_details.sort(key=lambda d: d[attr], reverse=True)
#     # Sort keys by order found in models.py
#     sorting_key = {s.value: idx for idx, s in enumerate(sorting_key.get(attr))}
#     # todo: have each key as its own key: value pair instead of combining them (i.e. k1, k2: value)
#     groups = groupby(word_details, lambda d: ['無'] if not d[attr] else d[attr])
#     groups = [(" ".join(k), list(g)) for k, g in groups]
#     groups.sort(key=lambda k: sorting_key.get(k[0], 100))
#     groups = [('所有', list(chain.from_iterable(w[1] for w in groups)))] + groups
#     for i in range(len(groups)):
#         groups[i][1].sort(key=lambda d: (d['item_freq'], d['item_name']),
#                           reverse=True)  # Sort within each group by frequency, then alphabetical order
#     groups = OrderedDict(groups)
#     logger.debug(f'Compiling complete.')
#     return groups


def _compile_attr_groups(word_details: List[dict], attr: str) -> Dict[str, List[dict]]:
    sorting_key = {
        'word_class': Sense.WordClassChoices,
        'focus': Sense.FocusChoices
    }
    logger.debug(f'Compiling {attr}')
    groups = {key.value: list() for key in list(sorting_key.get(attr))}
    groups['無'] = list()

    for word in word_details:
        features = word.get(attr)
        if not features:
            groups['無'].append(word)
            continue
        for f in features:
            groups[f].append(word)

    merged = {'所有': list(chain.from_iterable(g for g in groups.values()))}
    groups = {**merged, **groups}
    for group in groups:
        groups[group].sort(key=lambda d: (d['item_freq'], d['item_name']),
                           reverse=True)  # Sort within each group by frequency, then alphabetical order
    logger.debug(f'Compiling complete.')
    return groups


def build_item_root_freq(include_examples: bool) -> dict:
    word_freq = Counter()
    root_freq = Counter()

    word_details, not_found = [], []

    sent_num, word_num = 0, 0

    files = TextFile.objects.all()

    # Get text from uploaded files
    path = Path('test_dict_sent_split.txt')
    if path.exists():
        path.unlink()
    for file in files:
        text = file.read_and_decode()

        sent_num += len(_split_by_sent_boundary(text))
        word_num += len(_split_by_word_boundary(text))

        text = PUNCTUATION_RE.sub(' ', text).lower().split()
        word_freq.update(text)

    if include_examples:
        examples = Example.objects.all().values_list('sentence', flat=True)
        for text in examples:
            sent_num += len(_split_by_sent_boundary(text))
            word_num += len(_split_by_word_boundary(text))

            text = PUNCTUATION_RE.sub('', text).lower().split()
            word_freq.update(text)

    # One headword can have multiple senses. Use .distinct() to only count a headword once.
    # Some senses don't have a root, so get the earliest sense since it most likely has one.
    senses = Sense.objects.all().select_related('headword').values(
        'root',
        'focus',
        'word_class',
        'headword__headword',
        'headword__variant',
    ).order_by('headword__headword', '-root').distinct('headword__headword')

    for idx, (word, freq) in enumerate(word_freq.items()):
        for sense in senses:
            hw = sense.get('headword__headword')
            variant = sense.get('headword__variant')
            if word == hw or word in variant:
                query = sense
                root = query.get('root')
                focus = query.get('focus')
                word_class = query.get('word_class')
                if root:
                    root_freq[root] += freq

                word_details.append({
                    'item_name': word,
                    'item_freq': freq,
                    'root': root,
                    'root_freq': None,
                    'focus': focus,
                    'word_class': word_class,
                    'variant': variant,
                })
                break
        else:
            not_found.append({
                'item_name': word,
                'item_freq': freq,
                'root': '',
                'root_freq': '',
                'focus': '',
                'word_class': '',
                'variant': '',
            })
        if idx % 500 == 0:
            logger.debug(f"Completed {idx} of {len(word_freq)}")

    for word in word_details:
        word['root_freq'] = root_freq.get(word['root'])

    word_class_groups = _compile_attr_groups(word_details, 'word_class')
    focus_groups = _compile_attr_groups(word_details, 'focus')

    results = {
        # 'word_details': word_details,
        'word_class_groups': word_class_groups,
        'focus_groups': focus_groups,
        'not_found': not_found,
        'word_num': word_num,
        'sent_num': sent_num,
        'include_examples': include_examples,
    }
    return results
