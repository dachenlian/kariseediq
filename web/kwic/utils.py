from pathlib import Path
import pickle
import re
import string
from types import GeneratorType

from django.db.models import Q
from nltk.text import Text

from core.models import Headword, Example
from freqdist.models import TextFile

KWIC_PATH = Path(__file__).parent / 'static/kwic/kwic.pkl'


def _build_variant_dict() -> dict:
    variant_dict = {}
    for h in Headword.objects.filter(~Q(variant=[''])):
        headword: str = h.headword
        variant: list = h.variant
        variant_dict[headword] = variant
    return variant_dict


def _add_variant(words: GeneratorType) -> list:
    new_words = []
    variant_dict = _build_variant_dict()

    for word in words:
        vs = variant_dict.get(word)
        if vs:
            new_words.append(word)
            for v in vs:
                new_words.extend(['(', v, ')'])
        else:
            new_words.append(word)
    return new_words


def build_kwic(query, width, include_examples=False):
    pat_one = r"(\w+)([{}])".format(string.punctuation)  # add space between char and punctuation
    pat_two = r"([{}])(\w+)".format(string.punctuation)  # add space between punctuation and char

    files = TextFile.objects.all()
    texts = " ".join(text.read_and_decode() for text in files)
    texts = re.sub('\n', ' ', texts).strip()
    texts = re.sub(pat_one, r'\1 \2', texts)
    texts = re.sub(pat_two, r'\1 \2', texts)
    word_gen = (word for word in texts.split())
    words = _add_variant(word_gen)
    text = Text(words)
    conc_list = text.concordance_list(query, width=width, lines=9999999)  # show all lines
    with KWIC_PATH.open('wb') as f:
        d = {
            'query': query,
            'conc_list': conc_list
        }
        pickle.dump(d, f)
    return conc_list
