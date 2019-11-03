import csv
import pickle
import datetime

from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.views import View
from django.views.generic import DeleteView
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.urls import reverse_lazy

from .forms import TextFileUploadForm
from .models import TextFile
from . import utils

RESULTS_DIR = Path(settings.BASE_DIR) / 'freqdist' / 'static' / 'freqdist' / 'results'
if not RESULTS_DIR.exists():
    RESULTS_DIR.mkdir(parents=True)
FILE_NAME = 'freq_results.pkl'
FILE_PATH = RESULTS_DIR.joinpath(FILE_NAME)


class TextFileUploadView(View):

    def get(self, request):
        text_list = TextFile.objects.all()
        return render(self.request, 'freqdist/upload.html', context={'text_list': text_list})

    def post(self, request):
        form = TextFileUploadForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            text_file = form.save(commit=False)
            text_file.name = self.request.FILES.get('file').name
            text_file.save()
            data = {'is_valid': True, 'name': text_file.name, 'url': text_file.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)


class TextSingleDeleteView(DeleteView):
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


class TextAllDeleteView(View):
    success_url = reverse_lazy('freq:upload')
    success_message = "All texts successfully deleted!"

    def post(self, request, *args, **kwargs):
        TextFile.objects.all().delete()
        texts_path = Path(settings.MEDIA_ROOT) / 'freq'
        for text in texts_path.iterdir():
            text.unlink()
        messages.success(request, self.success_message)
        return redirect(self.success_url)


class FreqResultsView(View):
    def get(self, request, *args, **kwargs):
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
            results['word_details'].sort(
                key=lambda d: 0 if not d.get(sort_key) else d.get(sort_key),  # Some root_freq are None
                reverse=sort_dir)

        return render(request, 'freqdist/results.html', context=results)


def export_results_to_csv(request):
    with FILE_PATH.open('rb') as f:
        results = pickle.load(f)
    word_details = results.get('word_details')
    date = results.get('date')
    filename = f'freq_results.csv'

    fieldnames = word_details[0].keys()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    writer = csv.DictWriter(response, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(word_details)
    return response
