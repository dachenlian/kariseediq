from django.views.generic import View
from django.shortcuts import render

from .utils import build_kwic


class KwicView(View):
    template_name = 'kwic/index.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        if query:
            width = int(request.GET.get('width'))
            text = build_kwic()
            conc_list = text.concordance_list(query, width=width, lines=999999)  # show all lines
            print(len(conc_list))
            context = {
                'conc_list': conc_list,
            }
            return render(request, self.template_name, context=context)
        else:
            return render(request, self.template_name)
