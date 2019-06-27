import logging

from django import forms
from django.forms import ModelForm, inlineformset_factory
from django.utils.datastructures import MultiValueDict
from django.forms.widgets import SelectMultiple
from django.core.exceptions import ValidationError

from .models import Headword, Sense, Phrase, Example


logger = logging.getLogger(__name__)


class HeadwordForm(ModelForm):
    class Meta:
        model = Headword
        fields = ('headword', 'variant', 'is_root',)
        labels = {
            'is_root': 'Is root?',
        }


# https://stackoverflow.com/questions/12144475/displaying-multiple-rows-and-columns-in-django-crispy-forms
class SenseForm(ModelForm):
    headword = forms.CharField(max_length=255)

    class Meta:
        model = Sense
        fields = ('root', 'root_sense_no', 'headword_sense_no',
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
            'headword_sense_no': forms.HiddenInput(),
            'root': forms.widgets.TextInput(attrs={'class': 'basicAutoComplete', 'autocomplete': 'off'}),
            'root_sense_no': forms.widgets.TextInput(attrs={'class': 'typeahead'}),
            'word_class': SelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'}),
            'focus': SelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'}),
            'tag': SelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'}),
            'grammar_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
            'cultural_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
        }

    def clean_word_class(self):
        print('='*40)
        print("Inside clean word class!")
        data = self.cleaned_data['word_class']
        print(data)
        return data
    # def clean_word_class(self):
    #     data = self.cleaned_data['word_class']
    #     print('='*40)
    #     print(data)
    #
    # def clean(self):
    #     cleaned_data = super().clean()
    #     print("="*40)
    #     return cleaned_data
    #
    def clean_tag(self):
        print("Inside cleaning tag!!!")
        data = self.cleaned_data['tag']
        print(data)
        return data
    #
    # def clean_focus(self):
    #     print("Inside clean focus!!!")
    #     data = self.cleaned_data['focus']
    #     print(data)
    #     return data
    #
    # def clean_word_class(self):
    #     print("Inside clean word class!!!")
    #     data = self.cleaned_data['word_class']
    #     print('='*40)
    #     print(data)

    #
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['root_sense_no'].required = True

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


class SenseUpdateForm(SenseForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('headword')
        # self.fields['headword'].disabled = True
        self.fields['headword_sense_no'].disabled = True

    class Meta(SenseForm.Meta):
        fields = SenseForm.Meta.fields + ('headword_sense_no',)
        # exclude = ('headword', )



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
