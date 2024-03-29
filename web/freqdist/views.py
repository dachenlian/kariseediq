import csv
import datetime
import logging
from itertools import chain
import pickle
from typing import List

from pathlib import Path

import chardet
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views import View
from django.views.generic import DeleteView
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode

from .forms import TextFileUploadForm
from .models import TextFile
from . import utils

RESULTS_DIR = Path(settings.BASE_DIR) / 'freqdist' / 'static' / 'freqdist' / 'results'
if not RESULTS_DIR.exists():
    RESULTS_DIR.mkdir(parents=True)
FILE_NAME = 'freq_results.pkl'
FILE_PATH = RESULTS_DIR.joinpath(FILE_NAME)

logger = logging.getLogger(__name__)


class TextFileUploadView(LoginRequiredMixin, View):
    template_name = 'freqdist/simple-upload.html'

    def get(self, request):
        text_list = TextFile.objects.all()
        form = TextFileUploadForm()
        return render(self.request, self.template_name, context={'text_list': text_list, 'form': form})

    def post(self, request):
        form = TextFileUploadForm(self.request.POST, self.request.FILES)

        if form.is_valid():
            for file in self.request.FILES.getlist('file'):
                text_file = TextFile(file=file)
                text_file.name = file.name
                text_file.encoding = chardet.detect(file).get('encoding')
                text_file.save()

        return redirect(reverse('freqdist:upload'))


class TextSingleDeleteView(LoginRequiredMixin, DeleteView):
    model = TextFile
    success_url = reverse_lazy('freq:upload')
    success_message = "Text successfully deleted!"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        path = Path(obj.file.path)
        if path.exists():
            path.unlink()
        messages.success(request, self.success_message)
        return super().delete(request, *args, **kwargs)


class TextAllDeleteView(LoginRequiredMixin, View):
    success_url = reverse_lazy('freq:upload')
    success_message = "All texts successfully deleted!"

    def post(self, request, *args, **kwargs):
        TextFile.objects.all().delete()
        texts_path = Path(settings.MEDIA_ROOT) / 'freq'
        for text in texts_path.iterdir():
            text.unlink()
        messages.success(request, self.success_message)
        return redirect(self.success_url)


class FreqResultsView(LoginRequiredMixin, View):
    selected_group = None

    def get(self, request, *args, **kwargs):
        group_list = ['word_class_groups', 'focus_groups']
        group_list.remove(self.selected_group)
        recalculate = request.GET.get('recalculate')
        include_examples = request.GET.get('includeExamples') == 'True'
        sort_key = request.GET.get('order-by')
        sort_dir = request.GET.get('dir') == 'desc'

        if recalculate or not FILE_PATH.exists():
            results = utils.build_item_root_freq(include_examples)
            now = datetime.datetime.now()
            results['date'] = now
            with FILE_PATH.open('wb') as f:
                pickle.dump(results, f)
        else:
            with FILE_PATH.open('rb') as f:
                results = pickle.load(f)

        if sort_key:
            for key in results[self.selected_group]:
                results[self.selected_group][key].sort(
                    key=lambda d: (0, d.get('item_name')) if not d.get(sort_key) else (  # Some root_freq are None
                        d.get(sort_key), d.get('item_name')),  # sort by frequency then alphabetically
                    reverse=sort_dir)

        results['groups'] = results.pop(self.selected_group)
        results['selected_group'] = self.selected_group
        for key in group_list:
            results.pop(key)

        return render(request, 'freqdist/grouped_results.html', context=results)


class FreqResultsWordClassView(FreqResultsView):
    selected_group = "word_class_groups"


class FreqResultsMorphoView(FreqResultsView):
    selected_group = "focus_groups"


class CoverageView(LoginRequiredMixin, View):
    template_name = "freqdist/coverage.html"

    def get(self, request, *args, **kwargs):
        coverage = utils.calculate_coverage()
        context = {
            'coverage_list': coverage,
        }
        return render(request, self.template_name, context=context)


def _format_csv_rows(results: List[dict]) -> List[dict]:
    formatted_rows = []
    for row in results:
        for key in row:
            if isinstance(row[key], list):
                row[key] = ", ".join(row[key])
        formatted_rows.append(row)

    return formatted_rows


@login_required
def export_results_to_csv(request):
    with FILE_PATH.open('rb') as f:
        results = pickle.load(f)
    group = request.GET.get('group')  # e.g. word_class or morphological (focus)
    tab = request.GET.get('tab')  # e.g. nouns or verbs
    date = results.get('date').strftime('%Y%m%d')
    logger.debug(f'{group}{tab}')
    if tab:
        word_details = results.get(group).get(tab)
        filename = f'{date}_{group}_{tab}_freq_results.csv'
    else:
        word_details = results.get(group)
        filename = f'{date}_{group}_freq_results.csv'
    # filename = 'freq_results.csv'
    not_found = results.get('not_found')
    word_details = _format_csv_rows(word_details)
    filename = f'{date}_{group}_freq_results.csv'
    fieldnames = word_details[0].keys()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(word_details)
    writer.writerows(not_found)
    return response
