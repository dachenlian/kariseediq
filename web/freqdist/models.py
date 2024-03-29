import chardet
from django.db import models


class TextFile(models.Model):
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='uploads/freq/')
    encoding = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def _open_with_correct_encoding(file: bytes):
        encoding = chardet.detect(file).get('encoding')
        file = file.decode(encoding)
        return file

    def read_and_decode(self, as_list=False):
        text = self.file.read().decode(self.encoding).splitlines()
        if as_list:
            return text
        return ".".join(text)
