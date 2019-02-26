from django.db import models


class TextFile(models.Model):
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField(upload_to='uploads/freq/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
