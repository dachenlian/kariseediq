from django.shortcuts import render
from django.views.generic import View

from .utils import get_collocates


class CollocationView(View):
    template_name = 'collocations/index.html'

    def get(self, request, *args, **kwargs):
        ngram = request.GET.get('n-gram')
        assoc_measure = request.GET.get('assoc-measure')
        if ngram:
            collocations = get_collocates(ngram, assoc_measure)
            context = {
                'collocations': collocations,
            }
            return render(self.request, self.template_name, context=context)
        return render(self.request, self.template_name)




