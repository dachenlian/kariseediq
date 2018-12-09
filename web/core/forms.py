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

    # itemName = forms.CharField(max_length=255, label='Item name')
    # wordClass = MultiSelectFormField(max_length=255, label='Word class', choices=Entry.WORDCLASS_CHOICES, required=False)
    # variant = forms.CharField(max_length=255, label='Variant', required=False)
    # isPlant = forms.BooleanField(initial=False, label='Is plant', required=False)
    # toda = forms.CharField(max_length=255, label='Toda', required=False)
    # truku = forms.CharField(max_length=255, label='Truku', required=False)
    # isRoot = forms.BooleanField(initial=False, label='Is root', required=False)
    # meaning = forms.CharField(max_length=255, label='Meaning', required=False)
    # meaningEn = forms.CharField(max_length=255, label='Meaning (English)', required=False)
    # sentence = forms.CharField(max_length=255, label='Sentence', required=False)
    # sentenceCh = forms.CharField(max_length=255, label='Sentence (Chinese)', required=False)
    # sentenceEn = forms.CharField(max_length=255, label='Sentence (English)', required=False)
    # wordRoot = forms.CharField(max_length=255, label='Word root', required=False)
    # tagging = MultiSelectFormField(choices=Entry.TAGGING_CHOICES, label='Tagging', required=False)

    class Meta:
        model = Entry
        fields = ('itemName', 'wordRoot', 'variant', 'toda', 'truku',
                  'isPlant', 'isRoot', 'meaning', 'meaningEn', 'sentence',
                  'sentenceCh', 'sentenceEn', 'wordClass', 'tagging')
        labels = {
            'itemName': 'Item name',
            'wordClass': 'Word root',
            'isPlant': 'Is plant',
            'isRoot': 'Is root',
            'meaningEn': 'Meaning (English)',
            'sentenceEn': 'Sentence (English)',
            'sentenceCh': 'Sentence (Chinese)',
            'wordRoot': 'Word root',
        }
        widgets = {
            'sentence': forms.TextInput,
            'sentenceCh': forms.TextInput,
            'sentenceEn': forms.TextInput,
            'tagging': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'wordClass': forms.Select,
        }
