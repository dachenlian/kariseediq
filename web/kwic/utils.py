from pathlib import Path
import pickle
import re
import string
from typing import Generator, Tuple, List, Set

from django.db.models import Q
from nltk.text import Text, ConcordanceLine, ConcordanceIndex

from core.models import Headword, Example
from freqdist.models import TextFile

KWIC_PATH = Path(__file__).parent / 'static/kwic/kwic.pkl'
if not KWIC_PATH.parent.exists():
    KWIC_PATH.parent.mkdir(parents=True)


def _get_texts(include_examples: bool) -> str:
    files = TextFile.objects.all()
    texts = " ".join(text.read_and_decode() for text in files)
    if include_examples:
        examples = " ".join(Example.objects.all().values_list('sentence', flat=True))
        texts += " " + examples

    return texts


def _clean_texts(texts: str) -> str:
    pat_one = r"(\w+)([{}])".format(string.punctuation)  # add space between char and punctuation
    pat_two = r"([{}])(\w+)".format(string.punctuation)  # add space between punctuation and char

    texts = re.sub('\n', ' ', texts).strip()
    texts = re.sub(pat_one, r'\1 \2', texts)
    texts = re.sub(pat_two, r'\1 \2', texts)
    return texts


def _build_conc_lines(t: List[str], ql: List[str], intersects: Set[int], width: int) -> List[ConcordanceLine]:
    conc_lines = []
    for offset in intersects:
        left = t[max(offset - width, 0):offset]
        center = t[offset:(offset + len(ql))]
        right = t[(offset + len(ql)):(offset + len(ql) + width)]
        left_print = " ".join(left)
        right_print = " ".join(right)
        center_print = " ".join(center)
        line_print = " ".join([left_print, center_print, right_print])
        conc_line = ConcordanceLine(
            left=left,
            query=center_print,
            right=right,
            offset=offset,
            left_print=left_print,
            right_print=right_print,
            line=line_print
        )
        conc_lines.append(conc_line)

    return conc_lines


def _build_variant_dict() -> dict:
    variant_dict = {}
    for h in Headword.objects.filter(~Q(variant=[''])):
        headword: str = h.headword
        variant: list = h.variant
        variant_dict[headword] = variant
    return variant_dict


def _add_headword_variants(words: Generator) -> list:
    """Add variants of headwords within texts"""
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


def _get_normalized_offsets(c: ConcordanceIndex, qp: List[str]) -> List[List[int]]:
    offsets_norm = []
    offsets = [c.offsets(q) for q in qp]
    for i in range(len(qp)):
        offsets_norm.append([x - i for x in offsets[i]])

    return offsets_norm


def _sort_kwic(kwic: list, side: str = 'left', window: int = 2):
    if side == 'left':
        kwic.sort(key=lambda line: [w.lower() for w in line.left[-window:]])
    else:
        kwic.sort(key=lambda line: [w.lower() for w in line.right[:window]])
    return kwic


# def build_kwic(query: str, width: int, side: str = 'left', window: int = 2, include_examples=False) -> Tuple[list, int]:
#     """
#     Build a concordance.
#     :param query: A word or phrase to be searched
#     :param width: Set the number of characters on either side of the query
#     :param side: Sort results either by the left or right context
#     :param window: Sort the above selected side by the nth token starting from the query
#     :param include_examples: Include dictionary examples
#     :return: A concordance list and the total number of results returned
#     """
#     texts = _get_texts(include_examples)
#     texts = _clean_texts(texts)
#     word_gen = (word for word in texts.split())
#     words = _add_headword_variants(word_gen)
#     text = Text(words)
#     conc_list = text.concordance_list(query, width=width, lines=9999999)  # show all lines
#     conc_list = _sort_kwic(conc_list, side=side, window=window)
#     conc_len = len(conc_list)
#
#     with KWIC_PATH.open('wb') as f:
#         d = {
#             'query': query,
#             'conc_list': conc_list
#         }
#         pickle.dump(d, f)
#     return conc_list, conc_len


def build_kwic(query: str, width: int, side: str = 'left', window: int = 2, include_examples=False) -> Tuple[list, int]:
    """
    Build a concordance.
    :param query: A word or phrase to be searched
    :param width: Set the number of characters on either side of the query
    :param side: Sort results either by the left or right context
    :param window: Sort the above selected side by the nth token starting from the query
    :param include_examples: Include dictionary examples
    :return: A concordance list and the total number of results returned
    """
    texts = _get_texts(include_examples)
    texts = _clean_texts(texts)
    word_gen = (word for word in texts.split())
    words = _add_headword_variants(word_gen)

    # Using this instead of Text.concordance_list() because it doesn't support multi-word searches.
    # https://stackoverflow.com/a/34252075/7428193
    ci = ConcordanceIndex(words)
    query_list = query.split()
    offsets_norm = _get_normalized_offsets(ci, query_list)
    # Finds the indexes that are common between all lists, i.e., the query
    intersects = set(offsets_norm[0]).intersection(*offsets_norm[1:])
    conc_list = _build_conc_lines(words, query_list, intersects,  width)
    conc_list = _sort_kwic(conc_list, side=side, window=window)
    conc_len = len(conc_list)

    with KWIC_PATH.open('wb') as f:
        d = {
            'query': query,
            'conc_list': conc_list
        }
        pickle.dump(d, f)
    return conc_list, conc_len
