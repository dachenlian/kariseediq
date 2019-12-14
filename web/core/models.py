import datetime
from enum import Enum

from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Headword(models.Model):
    headword = models.CharField(max_length=255)
    user = models.CharField(max_length=255, blank=True, default="")
    only_letters = models.CharField(max_length=255, default="")  # used for sorting by letters only
    is_root = models.BooleanField(blank=True, default=False)
    created_date = models.DateField(default=datetime.date.today)
    modified_date = models.DateTimeField(auto_now=True)
    variant = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    def __str__(self):
        return self.headword

    def get_absolute_url(self):
        return reverse('core:update_headword', kwargs={'pk': self.id})

    class Meta:
        unique_together = ('headword', 'is_root')
        indexes = [
            models.Index(fields=['headword']),
            models.Index(fields=['variant'])
        ]


class Sense(models.Model):
    class FocusChoices(Enum):
        NOUN = '名詞性標記'
        DE_THEM = 'de-（某某）他們'
        K_ = 'k-'
        KN_NOUN = 'kn-名詞性標記'
        KN_ = 'kn-'
        SK_DEAD = 'sk-已過世'
        COMPOUND_WORD = '複合詞'
        COMPOUND_FORM = '複合型式'
        REDUP_CV = '重疊CV'
        REDUP_CVCV = '重疊CVCV'
        ZERO = '零焦點標記'
        AGENT = '主事焦點'
        PATIENT = '受事焦點'
        PATIENT_IMPERATIVE = '受事焦點（-i/-e/-o祈使）'
        N_PERFECT = '<n>完成貌'
        LOCATIVE = '處所焦點'
        REF_BENE = '參考焦點（受惠）'
        REF_INSTRUMENTAL = '參考焦點（工具）'
        REF_CAUSAL = '參考焦點（因為）'
        REF_IMPERATIVE = '參考焦點（-ani/-ane/-ano祈使）'
        REF_OTHER = '參考焦點（其他）'
        M_MP_M_FUTURE = 'm-/mp-/<m>未來'
        MG_RESEMBLE = 'mg-像；猶如'
        MK_WANT = 'mk-想'
        MN = 'mn-'
        N_BELONG = 'n-屬於'
        P_MAKE = 'p-使動'
        P_FUTURE = 'p-未來'
        P_ = 'p-'  # todo: should be removed
        PN = 'pn-'
        T_ = 't-'
        TG_ = 'tg-'
        PREFIX = '前綴'
        OTHER = '其他'

    class WordClassChoices(Enum):
        NOUN = '名詞'
        PRONOUN = '代名詞'
        CASE_MARKER = '格位標記'
        VERB = '動詞'
        PASSIVE_VERB = '靜態動詞'
        ADVERBIAL_VERB = '副詞性動詞'
        AUX_VERB_TIME = '助動詞（時貌）'
        ADVERB = '副詞'
        # ACTIVE_VERB = '動態動詞'
        CONJUNCTION = '連接詞'
        INTERROGATIVE = '疑問詞'
        NEGATION = '否定詞'
        COUNT = '數詞'
        DEMONSTRATIVE = '指示詞'
        PARTICLE = '助詞'
        INTERJECTION = '嘆詞'
        MULTI = '多重詞性'
        OTHER = '其它'

    class TagChoices(Enum):
        HAN_BORROWED = '漢語借字'
        JP_BORROWED = '日語借字'
        MIN_BORROWED = '閩南語借字'
        PLANT = '植物'
        NATURE = '自然'
        QUANTIFIER = '計量'
        HUNTING = '狩獵'
        TEXTILE = '織布服飾'
        TRANSPORTATION = '交通'
        RELATIVE = '親屬稱謂'
        EVERYDAY = '日常生活（含用品）'
        ANIMAL = '動物'
        BUILDING = '建築'
        BODY = '身體'
        AGRICULTURE = '農耕'
        RELIGION = '宗教'
        FOOD = '食物'
        INSECT = '昆蟲'

    headword = models.ForeignKey(Headword, related_name='senses', on_delete=models.CASCADE)
    headword_sense_no = models.PositiveSmallIntegerField(default=1)
    root = models.CharField(max_length=255, blank=True, default="")
    root_sense_no = models.PositiveSmallIntegerField(blank=True, null=True)
    user = models.CharField(max_length=255, blank=True, default="")
    created_date = models.DateField(default=datetime.date.today)
    modified_date = models.DateTimeField(auto_now=True)
    meaning = models.CharField(max_length=255, blank=True, default="")
    meaning_en = models.CharField(max_length=255, blank=True, default="")
    main_meaning_word_class = models.CharField(max_length=255, blank=True, default="")
    word_class = ArrayField(
        models.CharField(max_length=255, choices=[(w.value, w.value) for w in WordClassChoices]),
        default=list)
    cultural_notes = models.CharField(max_length=255, blank=True, default="")
    focus = ArrayField(models.CharField(max_length=255, choices=[(f.value, f.value) for f in FocusChoices]),
                       default=list)
    char_strokes_first = models.CharField(max_length=255, blank=True, default="")  # strokes for first char of meaning
    char_strokes_all = models.CharField(max_length=255, blank=True, default="")  # strokes for all chars of meaning
    frequency = models.IntegerField(blank=True, default=0)
    picture = models.ImageField(upload_to='pictures/', blank=True)
    sound = models.FileField(upload_to='sound/', blank=True)
    grammar_notes = models.CharField(max_length=255, blank=True, default="")  # 語法註記
    refer_to = models.CharField(max_length=255, blank=True, default="")  # 參照
    tag = ArrayField(models.CharField(max_length=255, choices=[(t.value, t.value) for t in TagChoices]),
                     default=list)  # 標籤
    toda = models.CharField(max_length=255, blank=True, default="")
    truku = models.CharField(max_length=255, blank=True, default="")

    class Meta:
        unique_together = ('headword', 'headword_sense_no')
        ordering = ['headword_sense_no']

    def __str__(self):
        return f"{self.headword.headword} ({self.headword_sense_no}): {self.meaning}"

    def get_absolute_url(self):
        return reverse('core:update_sense', kwargs={'pk': self.headword.id, 'sense': self.headword_sense_no})


class Example(models.Model):
    """Example sentence for a sense."""
    sense = models.ForeignKey(Sense, on_delete=models.CASCADE, related_name='examples')
    sentence = models.TextField(blank=True, default="")
    sentence_en = models.TextField(blank=True, default="")
    sentence_ch = models.TextField(blank=True, default="")
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sentence} / {self.sentence_ch}'


class Phrase(models.Model):
    """Phrase for a dictionary sense."""
    sense = models.ForeignKey(Sense, on_delete=models.CASCADE, related_name='phrases')
    phrase = models.CharField(max_length=255, blank=True, default="")  # 詞組
    phrase_ch = models.CharField(max_length=255, blank=True, default="")
    phrase_en = models.CharField(max_length=255, blank=True, default="")
    modified_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.phrase} / {self.phrase_ch}'

