from pathlib import Path

from django.contrib import messages
from django.views import View
from django.views.generic import DeleteView
from django.shortcuts import render
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


