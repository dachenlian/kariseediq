from django.shortcuts import render
from django.views.generic import View

from .utils import get_collocates


class CollocationView(View):
    template_name = 'collocations/index.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        freq_filter = int(request.GET.get('freq_filter', 1))
        ngram = request.GET.get('ngram')
        assoc_measure = request.GET.get('assoc_measure')
        window_size = int(request.GET.get('window_size', 1))
        include_examples = request.GET.get('include_examples')
        if ngram:
            collocations = get_collocates(ngram,
                                          assoc_measure,
                                          include_examples,
                                          query=query,
                                          freq_filter=freq_filter,
                                          window_size=window_size)
            context = {
                'collocations': collocations,
            }
            return render(self.request, self.template_name, context=context)
        return render(self.request, self.template_name)




