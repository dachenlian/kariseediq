from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.views import View
from django.views.generic import DeleteView
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse_lazy

from .models import TextFile
from .forms import TextFileUploadForm


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
        return render(request, 'freqdist/results.html')

