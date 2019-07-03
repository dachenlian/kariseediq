from core.models import Headword
from freqdist.models import TextFile


def _add_variant(words):
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
