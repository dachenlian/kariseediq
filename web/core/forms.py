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
    # tag = forms.MultipleChoiceField(choices=Entry.TAG_CHOICES)

    class Meta:
        model = Entry
        fields = ('item_name', 'item_root', 'variant', 'toda', 'truku',
                  'toda_root', 'truku_root', 'meaning', 'meaning_en', 'focus',
                  'word_class', 'tag', 'grammar_notes', 'cultural_notes')
        labels = {
            'item_name': 'Item name',
            'word_class': 'Word class',
            'meaning': 'Meaning (Chinese)',
            'word_root': 'Word root',
        }


class CreateEntryForm(ModelForm):
    class Meta:
        model = Entry
        fields = UpdateEntryForm.Meta.fields
