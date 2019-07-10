import re
import string
from types import GeneratorType

from nltk.text import Text

from core.models import Headword, Example
from freqdist.models import TextFile


def _add_variant(words: GeneratorType) -> list:
    new_words = []
    variant_dict = {}
    for h in Headword.objects.all():
        headword: str = h.headword
        variant: list = h.variant
        variant_dict[headword] = variant

    for word in words:
        v = variant_dict.get(word)
        if v:
            vs = f"({''.join(v)})"
            new_words.append(f"{word} {vs}")
        else:
            new_words.append(word)
    return new_words


def build_kwic(include_examples=False):
    pat_one = r"(\w+)([{}])".format(string.punctuation)
    pat_two = r"([{}])(\w+)".format(string.punctuation)

    files = TextFile.objects.all()
    texts = " ".join(text.read_and_decode() for text in files)
    texts = re.sub('\n', ' ', texts).strip()
    texts = re.sub(pat_one, r'\1 \2', texts)
    texts = re.sub(pat_two, r'\1 \2', texts)
    word_gen = (word for word in texts.split())
    words = _add_variant(word_gen)
    return Text(words)

