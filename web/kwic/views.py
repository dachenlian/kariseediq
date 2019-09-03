import csv
from pathlib import Path
import pickle

from django.http import HttpResponse
from django.views.generic import View
from django.shortcuts import render

from .utils import build_kwic, KWIC_PATH


class KwicView(View):
    template_name = 'kwic/index.html'

    def get(self, request, *args, **kwargs):
        query = request.GET.get('query')
        if query:
            width = int(request.GET.get('width'))
            conc_list = build_kwic(query, width=width)
            context = {
                'conc_list': conc_list,
            }
            return render(request, self.template_name, context=context)
        else:
            return render(request, self.template_name)


def export_results_to_csv(request):
    with KWIC_PATH.open('rb') as f:
        d = pickle.load(f)
    conc_list = d.get('conc_list')
    query = d.get('query')
    filename = Path(f"KWIC_{query}.csv")
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    header = ['left', 'query', 'right']

    kwic_writer = csv.writer(response)
    kwic_writer.writerow(header)

    for row in conc_list:
        kwic_writer.writerow([
            row.left_print,
            query,
            row.right_print
        ])
    return response
