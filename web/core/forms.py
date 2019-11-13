import logging
import re

from django import forms
from django.utils.encoding import force_text
from django.forms import ModelForm, inlineformset_factory
from django.forms.widgets import SelectMultiple

from .models import Headword, Sense, Phrase, Example

logger = logging.getLogger(__name__)


class ArraySelectMultiple(SelectMultiple):
    # https://stackoverflow.com/questions/52830191/django-arrayfield-rendered-using-selectmultiple-not-showing-the-selected-optons
    def format_value(self, value):
        if value is None and self.allow_multiple_selected:
            return []
        if not isinstance(value, (tuple, list)):
            value = value.split(',')

        return [force_text(v) if v is not None else '' for v in value]


class HeadwordForm(ModelForm):
    class Meta:
        model = Headword
        fields = ('headword', 'variant', 'is_root',)
        labels = {
            'is_root': 'Is root?',
        }

    def clean_variant(self):
        data = self.cleaned_data['variant']
        if not data:
            return list()
        if ',' in str(data):
            return data
        data = re.split(r'[,;]', "".join(data))
        data = [s.strip() for s in data]
        return data


# https://stackoverflow.com/questions/12144475/displaying-multiple-rows-and-columns-in-django-crispy-forms
class SenseForm(ModelForm):
    headword = forms.CharField(max_length=255)

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['tag'].initial = self.instance.tag
    #     self.fields['word_class'].initial = self.instance.word_class

    class Meta:
        model = Sense
        fields = ('root', 'root_sense_no', 'headword_sense_no',
                  'meaning', 'meaning_en', 'word_class', 'cultural_notes',
                  'focus', 'picture', 'sound', 'truku', 'grammar_notes',
                  'refer_to', 'tag', 'toda',)
        labels = {
            'word_class': 'Word class',
            'meaning': 'Meaning (Chinese)',
            'meaning_en': 'Meaning (English)',
            'focus': '構詞標記',
            'word_root': 'Word root',
            'truku': 'Truku headword',
            'toda': 'Toda headword'
        }
        widgets = {
            'headword': forms.widgets.TextInput(attrs={'class': 'basicAutoComplete', 'autocomplete': 'off'}),
            'headword_sense_no': forms.HiddenInput(),
            'root': forms.widgets.TextInput(attrs={'class': 'basicAutoComplete', 'autocomplete': 'off'}),
            'root_sense_no': forms.widgets.TextInput(attrs={'class': 'typeahead'}),
            'word_class': ArraySelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'},
                                              choices=[(t.value, t.value) for t in Sense.WordClassChoices]
                                              ),
            'focus': ArraySelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'},
                                         choices=[(t.value, t.value) for t in Sense.FocusChoices]
                                         ),
            'tag': ArraySelectMultiple(attrs={'class': 'selectpicker', 'title': '-------'},
                                       choices=[(t.value, t.value) for t in Sense.TagChoices]
                                       ),
            'grammar_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
            'cultural_notes': forms.widgets.Textarea(attrs={'rows': 5, 'cols': 40}),
        }


class SenseUpdateForm(SenseForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('headword')
        # self.fields['headword'].disabled = True
        self.fields['headword_sense_no'].disabled = True

    class Meta(SenseForm.Meta):
        fields = SenseForm.Meta.fields + ('headword_sense_no', 'char_strokes_all', 'char_strokes_first')
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
