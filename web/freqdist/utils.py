import functools
from multiprocessing import Pool, cpu_count, Manager
import re
from collections import Counter

from django.db.models import Q

from .models import TextFile
from core.models import Headword, Example, Sense

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

    # Get text from uploaded files
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

    senses = Sense.objects.all().select_related('headword').values(
        'root',
        'focus',
        'word_class',
        'headword__headword',
        'headword__variant',
    )

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

    results = {
        'word_details': word_details,
        'word_num': word_num,
        'sent_num': sent_num,
        'include_examples': include_examples,
    }
    return results
