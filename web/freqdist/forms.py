from django import forms

from .models import TextFile


# class TextFileUploadForm(forms.Form):
#     file = forms.FileField(widget=forms.ClearableFileInput(
#         attrs={'multiple': True}
#     ))
class TextFileUploadForm(forms.ModelForm):
    class Meta:
        model = TextFile
        fields = ('file',)
