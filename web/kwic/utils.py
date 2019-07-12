import re
import string
from types import GeneratorType

from django.db.models import Q
from nltk.text import Text

from core.models import Headword, Example
from freqdist.models import TextFile


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
        v = variant_dict.get(word)
        if v:
            vs = f"({', '.join(v)})"
            new_words.append(f"{word} {vs}")
        else:
            new_words.append(word)
    return new_words


def build_kwic(include_examples=False):
    pat_one = r"(\w+)([{}])".format(string.punctuation)  # add space between char and punctuation
    pat_two = r"([{}])(\w+)".format(string.punctuation)  # add space between punctuation and char

    files = TextFile.objects.all()
    texts = " ".join(text.read_and_decode() for text in files)
    texts = re.sub('\n', ' ', texts).strip()
    texts = re.sub(pat_one, r'\1 \2', texts)
    texts = re.sub(pat_two, r'\1 \2', texts)
    word_gen = (word for word in texts.split())
    words = _add_variant(word_gen)
    return Text(words)
