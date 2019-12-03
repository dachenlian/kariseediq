import functools
import logging
from multiprocessing import Pool, cpu_count, Manager
from pathlib import Path
from typing import Sequence, Tuple
import re
from collections import Counter, OrderedDict
from itertools import groupby, chain

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


def build_item_root_freq(include_examples: bool) -> dict:
    word_freq = Counter()
    root_freq = Counter()

    word_details = []

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
        if idx % 500 == 0:
            print(f"Completed {idx} of {len(word_freq)}")

    for word in word_details:
        word['root_freq'] = root_freq.get(word['root'])

    word_details.sort(key=lambda d: d['word_class'], reverse=True)
    word_class_sorting_key = {w.value: idx for idx, w in enumerate(Sense.WordClassChoices)}
    logger.debug(word_class_sorting_key)
    logger.debug('代名詞' in word_class_sorting_key)
    groups = groupby(word_details, lambda d: ['無'] if not d['word_class'] else d['word_class'])
    word_class_groups = [(" ".join(k), list(g)) for k, g in groups]
    word_class_groups.sort(key=lambda k: word_class_sorting_key.get(k[0], 100))
    word_class_groups = [('所有', list(chain.from_iterable(w[1] for w in word_class_groups)))] + word_class_groups
    for i in range(len(word_class_groups)):
        word_class_groups[i][1].sort(key=lambda d: (d['item_freq'], d['item_name']), reverse=True)
    word_class_groups = OrderedDict(word_class_groups)
    results = {
        'word_details': word_details,
        'word_class_groups': word_class_groups,
        'word_num': word_num,
        'sent_num': sent_num,
        'include_examples': include_examples,
    }
    return results
