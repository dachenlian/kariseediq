from django.views import View
from django.shortcuts import render
from django.http import JsonResponse

from .models import TextFile
from .forms import TextFileUploadForm


class TextFileUploadView(View):

    def get(self, request):
        text_list = TextFile.objects.all()
        return render(self.request, 'freqdist/upload', {'text_list', text_list})

    def post(self, request):
        form = TextFileUploadForm(self.request.POST, self.request.FILES)
        if form.is_valid():
            text_file = form.save(commit=False)
            text_file.name = self.request.FILES.get('file').name
            data = {'is_valid': True, 'name': text_file.name, 'url': text_file.file.url}
        else:
            data = {'is_valid': False}
        return JsonResponse(data)
