from django.shortcuts import render
from django.views.generic import View

# Create your views here.


class CollocationView(View):
    template_name = 'collocations/index.html'

    def get(self, request, *args, **kwargs):
        return render(self.template_name)




