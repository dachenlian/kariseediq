from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError

from .models import Headword, Sense, Phrase, Example


# https://stackoverflow.com/questions/12144475/displaying-multiple-rows-and-columns-in-django-crispy-forms
class EntryForm(ModelForm):
    # tag = forms.MultipleChoiceField(choices=Entry.TAG_CHOICES)

    class Meta:
        model = Entry
        fields = ('item_name', 'item_root', 'variant', 'toda', 'truku', 'sound', 'picture',
                  'phrase', 'phrase_en', 'phrase_ch', 'refer_to',
                  'toda_root', 'truku_root', 'meaning', 'meaning_en', 'focus',
                  'word_class', 'tag', 'grammar_notes', 'cultural_notes')
        labels = {
            'item_name': 'Item name',
            'word_class': 'Word class',
            'meaning': 'Meaning (Chinese)',
            'meaning_en': 'Meaning (English)',
            'word_root': 'Word root',
        }
        widgets = {
            'item_name': forms.widgets.TextInput(attrs={'class': 'basicAutoComplete', 'autocomplete': 'off'}),
            'item_root': forms.widgets.TextInput(attrs={'class': 'basicAutoComplete', 'autocomplete': 'off'}),
            'tag': forms.widgets.SelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'}),
            'grammar_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
            'cultural_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
        }

    def clean(self):
        cleaned_data = super().clean()
        item_name = cleaned_data.get('item_name')
        item_root = cleaned_data.get('item_root')

        if item_name == item_root:
            cleaned_data['is_root'] = True
        else:
            cleaned_data['is_root'] = False
        return cleaned_data

    # def clean_item_name(self):
    #     data = self.cleaned_data['item_name']
    #     if any(char.isdigit() for char in data):
    #         raise ValidationError('Item name cannot contain numbers')
    #     return data


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


ExampleFormSet = inlineformset_factory(
    parent_model=Entry,
    model=Example,
    form=ExampleForm,
    extra=2,
)


