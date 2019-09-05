import functools
from multiprocessing import Pool, cpu_count, Manager
import re
from collections import Counter

from django.db.models import Q

from .models import TextFile
from core.models import Headword, Example

sent_boundary = ['.', '。', '!', '！', '?', '？', ';', '；']
SENT_BOUNDARY_RE = re.compile(rf'[{"".join(sent_boundary)}]')

punctuations = "".join(['，', '。', '？', '！', '：', '；', '（', '）', '「', '』',
                        ',', '.', '?', '!', ':', ';', '(', ')', '"', '“',
                        '”', '~', '/', '-'])  # 共17個
PUNCTUATION_RE = re.compile(rf'[{"".join(punctuations)}]')


def _split_by_word_boundary(text):
    return text.split()


def _split_by_sent_boundary(text):
    text = SENT_BOUNDARY_RE.sub('.', text)
    return text.split('.')


def build_item_root_freq(include_examples: bool) -> dict:
    word_freq = Counter()
    root_freq = Counter()

    word_details = []

    sent_num, word_num = 0, 0

    files = TextFile.objects.all()

    for file in files:
        text = file.read_and_decode()

        sent_num += len(_split_by_sent_boundary(text))
        word_num += len(_split_by_word_boundary(text))

        text = PUNCTUATION_RE.sub('', text).lower().split()
        word_freq.update(text)

    if include_examples:
        examples = Example.objects.all().values_list('sentence', flat=True)
        for text in examples:
            sent_num += len(_split_by_sent_boundary(text))
            word_num += len(_split_by_word_boundary(text))

            text = PUNCTUATION_RE.sub('', text).lower().split()
            word_freq.update(text)

    print("Completed word_freq...")
    print(len(word_freq))

    for idx, (word, freq) in enumerate(word_freq.items()):
        query = Headword.objects.filter(Q(headword=word) |
                                        Q(variant__contains=[word])).prefetch_related('senses')
        if not query:
            continue
        else:
            query = query[0]
        sense = query.senses.all()[0]
        root = sense.root
        focus = sense.focus
        word_class = sense.word_class
        variant = query.variant
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

    results = {
        'word_details': word_details,
        'word_num': word_num,
        'sent_num': sent_num,
        'include_examples': include_examples,
    }
    return results


def get_word_details(q, freq, manager_dict=None):
    print(q, freq)
    # q, freq = word_freq_tup
    query = Headword.objects.filter(Q(headword=q) | Q(variant__contains=[q])).prefetch_related('senses')
    if not query:
        return
    else:
        query = query[0]
    sense = query.senses.all()[0]
    root = sense.root
    focus = sense.focus
    word_class = sense.word_class
    variant = query.variant

    if manager_dict:
        if root:
            manager_dict[q] += manager_dict.get(q, 0) + freq

    details = {
        'sense': sense,
        'root': root,
        'root_freq': None,
        'focus': focus,
        'word_class': word_class,
        'variant': variant
    }

    return details


def build_word_details_multiproc(word_freq):
    # root_freq = Manager().dict()
    with Pool(processes=int(cpu_count() * .75)) as pool:
        # get_word_details_partial = functools.partial(get_word_details, manager_dict=root_freq)
        # results = pool.starmap(get_word_details_partial, word_freq.items())
        # word_freq = [('usa', 1), ('lmamu', 46), ('iya', 151)] * 1000
        word_freq = list(word_freq.items())
        results = pool.starmap(get_word_details, word_freq)

    return results
    # for r in results:
    #     r['root_freq'] = root_freq.get(r['root'])
    # return results, root_freq


def build_item_root_freq_multiproc(include_examples: bool) -> dict:
    word_freq = Counter()

    sent_num, word_num = 0, 0

    files = TextFile.objects.all()

    for file in files:
        text = file.read_and_decode()

        sent_num += len(_split_by_sent_boundary(text))
        word_num += len(_split_by_word_boundary(text))

        text = PUNCTUATION_RE.sub('', text).lower().split()
        word_freq.update(text)

    if include_examples:
        examples = Example.objects.all().values_list('sentence', flat=True)
        for text in examples:
            sent_num += len(_split_by_sent_boundary(text))
            word_num += len(_split_by_word_boundary(text))

            text = PUNCTUATION_RE.sub('', text).lower().split()
            word_freq.update(text)

    print("Completed word_freq...")
    print(len(word_freq))
    word_details, root_freq = build_word_details_multiproc(word_freq)

    results = {
        'word_details': word_details,
        'word_num': word_num,
        'sent_num': sent_num,
        'include_examples': include_examples,
    }
    return results


def test_build_item_root_freq_multiproc(include_examples: bool) -> dict:
    word_freq = Counter()

    sent_num, word_num = 0, 0

    files = TextFile.objects.all()

    for file in files:
        text = file.read_and_decode()

        sent_num += len(_split_by_sent_boundary(text))
        word_num += len(_split_by_word_boundary(text))

        text = PUNCTUATION_RE.sub('', text).lower().split()
        word_freq.update(text)

    if include_examples:
        examples = Example.objects.all().values_list('sentence', flat=True)
        for text in examples:
            sent_num += len(_split_by_sent_boundary(text))
            word_num += len(_split_by_word_boundary(text))

            text = PUNCTUATION_RE.sub('', text).lower().split()
            word_freq.update(text)

    print("Completed word_freq...")
    print(len(word_freq))
    return word_freq


def get_word_details_test(q, freq):
    # q, freq = word_freq_tup
    query = Headword.objects.filter(Q(headword=q) | Q(variant__contains=[q])).prefetch_related('senses')
    if not query:
        return
    else:
        query = query[0]
    sense = query.senses.all()[0]
    root = sense.root
    focus = sense.focus
    word_class = sense.word_class
    variant = query.variant

    details = {
        'sense': sense,
        'root': root,
        'root_freq': None,
        'focus': focus,
        'word_class': word_class,
        'variant': variant
    }

    return details


def test_multiproc():
    queries = list(dict(test_build_item_root_freq_multiproc(False)).items())
    print(type(queries))
    print(type(queries[0]))

    with Pool(processes=int(cpu_count() * .75)) as pool:
        results = pool.starmap(get_word_details_test, queries)
    return results
