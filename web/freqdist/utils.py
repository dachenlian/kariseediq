import re
from collections import Counter

from django.db.models import Q

from .models import TextFile
from core.models import Headword

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


def build_item_root_freq() -> dict:
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

    # for idx, (word, freq) in enumerate(word_freq.items(), 1):
    #     query = Headword.objects.filter(Q(headword=word) |
    #                                     Q(variant__contains=word)
    #                                     ).prefetch_related('senses')
    #     if query.exists():
    #         sense = query[0].senses.all()[0]
    #         root = sense.root
    #         focus = sense.focus
    #         word_class = sense.word_class
    #         variant = query[0].variant
    #         if root:
    #             root_freq[root] += freq
    #
    #         word_details.append({
    #             'item_name': word,
    #             'item_freq': freq,
    #             'root': root,
    #             'root_freq': None,
    #             'focus': focus,
    #             'word_class': word_class,
    #             'variant': variant,
    #         })
    #     if idx % 500 == 0:
    #         print(f"Completed {idx} of {len(word_freq)}")
    # for word in word_details:
    #     word['root_freq'] = root_freq.get(word['root'])

    results = {
        'word_details': word_details,
        'word_num': word_num,
        'sent_num': sent_num
    }
    return results
