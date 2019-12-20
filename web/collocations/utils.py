import logging
import nltk
from nltk import collocations

from typing import List, Tuple

from freqdist.models import TextFile
from kwic.utils import clean_texts, get_texts
from core.models import Example


logger = logging.getLogger(__name__)


MEASURES_FINDERS_DICT = {
    'bigram': [
        collocations.BigramAssocMeasures(),
        collocations.BigramCollocationFinder,
    ],
    'trigram': [
        collocations.TrigramAssocMeasures(),
        collocations.TrigramCollocationFinder,
    ],
    'quadgram': [
        collocations.QuadgramAssocMeasures(),
        collocations.QuadgramCollocationFinder,
    ]
}


def get_collocates(ngram: str,
                   assoc_measure: str,
                   include_examples: bool,
                   query: str = None,
                   freq_filter: int = 3,
                   window_size: int = None,
                   limit: int = 1000) -> List[Tuple[str, str, int]]:
    measures, finder = MEASURES_FINDERS_DICT.get(ngram)
    texts = get_texts(include_examples)
    texts = clean_texts(texts)
    tokens = texts.split()
    finder = finder.from_words(tokens, window_size=window_size)
    if freq_filter:
        finder.apply_freq_filter(freq_filter)
    results = finder.score_ngrams(getattr(measures, assoc_measure))[:limit]
    if query:
        logger.debug(query)
        results = [result for result in results if query in (r.lower() for r in result[0])]  # case insensitive search
    results = [(finder.ngram_fd[result[0]],) + result for result in results]  # get freq for each ngram
    for i in range(len(results)):
        result = list(results[i])
        result[1] = f"({', '.join(result[1])})"
        results[i] = result
    return results


