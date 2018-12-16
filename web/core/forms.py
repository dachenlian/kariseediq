from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div
from multiselectfield import MultiSelectFormField

from django.forms import ModelForm
from .models import Entry


class Row(Div):
    css_class = "form-row"


# https://stackoverflow.com/questions/12144475/displaying-multiple-rows-and-columns-in-django-crispy-forms
class UpdateEntryForm(ModelForm):

    class Meta:
        model = Entry
        fields = ('item_name', 'item_root', 'variant', 'toda', 'truku',
                  'toda_root', 'truku_root', 'meaning', 'meaning_en', 'focus', 'sentence',
                  'sentence_ch', 'sentence_en', 'word_class', 'tag', 'grammar_notes', 'cultural_notes')
        labels = {
            'item_name': 'Item name',
            'word_class': 'Word class',
            'meaning': 'Meaning (Chinese)',
            'meaning_en': 'Meaning (English)',
            'sentence_en': 'Sentence (English)',
            'sentence_ch': 'Sentence (Chinese)',
            'word_root': 'Word root',
        }
        widgets = {
            'sentence': forms.TextInput,
            'sentence_ch': forms.TextInput,
            'sentence_en': forms.TextInput,
            'tag': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'word_class': forms.Select,
        }
