import nltk
from nltk import collocations

from typing import List, Tuple

from freqdist.models import TextFile
from kwic.utils import clean_texts


MEASURES_FINDERS_DICT = {
    'bigram': [
        collocations.BigramAssocMeasures(),
        collocations.BigramCollocationFinder,
    ],
    'trigram': [
        collocations.TrigramAssocMeasures(),
        collocations.TrigramCollocationFinder,
    ]
}


def get_collocates(ngram: str, assoc_measure: str) -> List[Tuple[str, str]]:
    measure, finder = MEASURES_FINDERS_DICT.get(ngram)
    files = TextFile.objects.all()
    texts = " ".join(text.read_and_decode() for text in files)
    texts = clean_texts(texts)
    tokens = texts.split()
    finder = finder.from_words(tokens)
    results = finder.nbest(getattr(measure, assoc_measure), 500)
    return results


