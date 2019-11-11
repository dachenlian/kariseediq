from pathlib import Path
import pickle
import re
import string
from typing import Generator, Tuple

from django.db.models import Q
from nltk.text import Text

from core.models import Headword, Example
from freqdist.models import TextFile

KWIC_PATH = Path(__file__).parent / 'static/kwic/kwic.pkl'
if not KWIC_PATH.parent.exists():
    KWIC_PATH.parent.mkdir(parents=True)


def get_texts(include_examples: bool) -> str:
    files = TextFile.objects.all()
    texts = " ".join(text.read_and_decode() for text in files)
    if include_examples:
        examples = " ".join(Example.objects.all().values_list('sentence', flat=True))
        texts += " " + examples

    return texts


def clean_texts(texts: str) -> str:
    pat_one = r"(\w+)([{}])".format(string.punctuation)  # add space between char and punctuation
    pat_two = r"([{}])(\w+)".format(string.punctuation)  # add space between punctuation and char

    texts = re.sub('\n', ' ', texts).strip()
    texts = re.sub(pat_one, r'\1 \2', texts)
    texts = re.sub(pat_two, r'\1 \2', texts)
    return texts


def _build_variant_dict() -> dict:
    variant_dict = {}
    for h in Headword.objects.filter(~Q(variant=[''])):
        headword: str = h.headword
        variant: list = h.variant
        variant_dict[headword] = variant
    return variant_dict


def _add_variant(words: Generator) -> list:
    new_words = []
    variant_dict = _build_variant_dict()

    for word in words:
        vs = variant_dict.get(word)
        if vs:
            new_words.append(word)
            for v in vs:
                new_words.extend(['(', v, ')'])  # add parentheses as separate items so concordance will find them
        else:
            new_words.append(word)
    return new_words


def _sort_kwic(kwic: list, side: str = 'left', window: int = 2):
    if side == 'left':
        kwic.sort(key=lambda line: [w.lower() for w in line.left[-window:]])
    else:
        kwic.sort(key=lambda line: [w.lower() for w in line.right[:window]])
    return kwic


def build_kwic(query: str, width: int, side: str = 'left', window: int = 2, include_examples=False) -> Tuple[list, int]:
    texts = get_texts(include_examples)
    texts = clean_texts(texts)
    word_gen = (word for word in texts.split())
    words = _add_variant(word_gen)
    text = Text(words)
    conc_list = text.concordance_list(query, width=width, lines=9999999)  # show all lines
    conc_list = _sort_kwic(conc_list, side=side, window=window)
    conc_len = len(conc_list)

    with KWIC_PATH.open('wb') as f:
        d = {
            'query': query,
            'conc_list': conc_list
        }
        pickle.dump(d, f)
    return conc_list, conc_len
