from django import forms

from django_file_form.forms import FileFormMixin, UploadedFileField

from .models import TextFile


class TextFileUploadForm(forms.Form):
    file = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'multiple': True}
    ))
# class TextFileUploadForm(FileFormMixin, forms.ModelForm):
#     input_file = UploadedFileField()
#
#     class Meta:
#         model = TextFile
#         fields = ('file',)
