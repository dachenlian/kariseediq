import nltk
from nltk import collocations

from freqdist.models import TextFile

BIGRAM_MEASURES = collocations.BigramAssocMeasures()
TRIGRAM_MEASURES = collocations.TrigramAssocMeasures()


