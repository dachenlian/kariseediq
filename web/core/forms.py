from django import forms

from django.forms import ModelForm
from .models import Entry, Example


# https://stackoverflow.com/questions/12144475/displaying-multiple-rows-and-columns-in-django-crispy-forms
class EntryForm(ModelForm):
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
            'meaning_en': 'Meaning (English)',
            'word_root': 'Word root',
        }


class EntryUpdateForm(EntryForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_name'].disabled = True


class ExampleForm(ModelForm):
    class Meta:
        model = Example
        fields = ['sentence', 'sentence_ch', 'sentence_en']
        labels = {
            'sentence_en': 'Sentence (English)',
            'sentence_ch': 'Sentence (Chinese)',
        }
        widgets = {
            'sentence': forms.TextInput,
            'sentence_ch': forms.TextInput,
            'sentence_en': forms.TextInput,
        }

