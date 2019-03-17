from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.core.exceptions import ValidationError

from .models import Headword, Sense, Phrase, Example


# https://stackoverflow.com/questions/12144475/displaying-multiple-rows-and-columns-in-django-crispy-forms
class SenseForm(ModelForm):
    # tag = forms.MultipleChoiceField(choices=Entry.TAG_CHOICES)

    class Meta:
        model = Sense
        fields = ('headword', 'headword_sense_no', 'root', 'root_sense_no',
                  'meaning', 'meaning_en', 'word_class', 'cultural_notes',
                  'focus', 'picture', 'sound', 'truku', 'grammar_notes',
                  'refer_to', 'tag', 'toda', 'toda_root', 'truku', 'truku_root',)
        labels = {
            'word_class': 'Word class',
            'meaning': 'Meaning (Chinese)',
            'meaning_en': 'Meaning (English)',
            'word_root': 'Word root',
        }
        widgets = {
            'headword': forms.widgets.TextInput(attrs={'class': 'basicAutoComplete', 'autocomplete': 'off'}),
            'root': forms.widgets.TextInput(attrs={'class': 'basicAutoComplete', 'autocomplete': 'off'}),
            'tag': forms.widgets.SelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'}),
            'grammar_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
            'cultural_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
        }

    # def clean(self):
    #     cleaned_data = super().clean()
    #     item_name = cleaned_data.get('item_name')
    #     item_root = cleaned_data.get('item_root')
    #
    #     if item_name == item_root:
    #         cleaned_data['is_root'] = True
    #     else:
    #         cleaned_data['is_root'] = False
    #     return cleaned_data

    # def clean_item_name(self):
    #     data = self.cleaned_data['item_name']
    #     if any(char.isdigit() for char in data):
    #         raise ValidationError('Item name cannot contain numbers')
    #     return data


class SenseUpdateForm(SenseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['headword'].disabled = True


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


class PhraseForm(ModelForm):
    class Meta:
        model = Phrase
        fields = ['phrase', 'phrase_ch', 'phrase_en']
        labels = {
            'phrase_ch': 'Phrase (Chinese)',
            'phrase_en': 'Phrase (English)',
        }


ExampleFormset = inlineformset_factory(
    parent_model=Sense,
    model=Example,
    form=ExampleForm,
    extra=2,
)

PhraseFormset = inlineformset_factory(
    parent_model=Sense,
    model=Phrase,
    form=PhraseForm,
    extra=2
)

