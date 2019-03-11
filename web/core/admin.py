from django.contrib import admin
from .models import Headword, Sense, Example, Phrase
# Register your models here.
admin.site.register(Headword)
admin.site.register(Sense)
admin.site.register(Example)
admin.site.register(Phrase)
