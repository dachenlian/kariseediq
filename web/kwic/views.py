from django.views.generic import View
from django.shortcuts import render


class KwicView(View):
    template_name = 'kwic/index.html'

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q')
        if q:
            pass
        else:
            return render(request, self.template_name)
