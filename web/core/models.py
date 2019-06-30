import datetime
from enum import Enum

from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields import ArrayField


class Headword(models.Model):
    headword = models.CharField(max_length=255, unique=True)
    user = models.CharField(max_length=255, blank=True, default="")
    only_letters = models.CharField(max_length=255, default="")  # used for sorting by letters only
    is_root = models.BooleanField(blank=True, default=False)
    created_date = models.DateField(default=datetime.date.today)
    modified_date = models.DateTimeField(auto_now=True)
    variant = ArrayField(models.CharField(max_length=255), default=list, blank=True)

    def __str__(self):
        return self.headword

    def get_absolute_url(self):
        return reverse('core:update_headword', kwargs={'hw': self.headword})


class Sense(models.Model):
    class FocusChoices(Enum):
        NOUN = '名詞性標記'
        DE_THEM = 'de-（某某）他們'
        KN_NOUN = 'kn-名詞性標記'
        SK_DEAD = 'sk-已過世'
        COMPOUND_WORD = '複合詞'
        COMPOUND_FORM = '複合型式'
        REDUP_CV = '重疊CV'
        REDUP_CVCV = '重疊CVCV'
        AGENT = '主事焦點'
        PATIENT = '受事焦點'
        PATIENT_IMPERATIVE = '受事焦點（祈使）'
        N_PERFECT = '<n>完成貌'
        LOCATIVE = '處所焦點'
        REF_BENE = '參考焦點（受惠）'
        REF_INSTRUMENTAL = '參考焦點（工具）'
        REF_CAUSAL = '參考焦點（因為）'
        REF_IMPERATIVE = '參考焦點（祈使）'
        REF_OTHER = '參考焦點（其他）'
        P_MOVE = 'p-使動'
        P_FUTURE = 'p-未來'
        M_FUTURE = 'm-未來'
        MG_RESEMBLE = 'mg-像；猶如'
        N_BELONG = 'n-屬於'
        PN = 'pn-'
        MN = 'mn-'
        T = 't-'
        PREFIX = '前綴'
        OTHER = '其他'
        GRAMMATICAL_GENDER = '名詞性標記'
        REFERENCE = '參考焦點'
        ZERO = '零焦點標記'

    class WordClassChoices(Enum):
        NOUN = '名詞'
        PRONOUN = '代名詞'
        CASE_MARKER = '格位標記'
        ACTIVE_VERB = '動態動詞'
        PASSIVE_VERB = '靜態動詞'
        ADVERBIAL_VERB = '副詞性動詞'
        AUX_VERB_TIME = '助動詞（時貌）'
        VERB = '動詞'
        ADVERB = '副詞'
        CONJUNCTION = '連接詞'
        INTERROGATIVE = '疑問詞'
        NEGATION = '否定詞'
        COUNT = '數詞'
        DEMONSTRATIVE = '指示詞'
        PARTICLE = '助詞'
        INTERJECTION = '嘆詞'
        MULTI = '多重詞性'
        OTHER = '其他'

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
    word_class = ArrayField(models.CharField(max_length=255, blank=True, choices=[(w.value, w.value) for w in WordClassChoices]),
                            # choices=[(w.value, w.value) for w in WordClassChoices],
                            default=list,
                            blank=True)
    cultural_notes = models.CharField(max_length=255, blank=True, default="")
    focus = ArrayField(models.CharField(max_length=255, blank=True, choices=[(f.value, f.value) for f in FocusChoices]),
                       # choices=[(f.value, f.value) for f in FocusChoices],
                       default=list,
                       blank=True)
    char_strokes_first = models.CharField(max_length=255, blank=True, default="")  # no. of strokes for char of meaning
    char_strokes_all = models.CharField(max_length=255, blank=True, default="")  # no. of strokes for all chars
    frequency = models.IntegerField(blank=True, default=0)
    picture = models.ImageField(upload_to='pictures/', blank=True)
    sound = models.FileField(upload_to='sound/', blank=True)
    grammar_notes = models.CharField(max_length=255, blank=True, default="")  # 語法註記
    refer_to = models.CharField(max_length=255, blank=True, default="")  # 參照
    tag = ArrayField(models.CharField(max_length=255, blank=True, choices=[(t.value, t.value) for t in TagChoices]),
                     # choices=[(t.value, t.value) for t in TagChoices],
                     default=list,
                     blank=True)  # 標籤
    toda = models.CharField(max_length=255, blank=True, default="")
    toda_root = models.CharField(max_length=255, blank=True, default="")  # todar
    truku = models.CharField(max_length=255, blank=True, default="")
    truku_root = models.CharField(max_length=255, blank=True, default="")  # trukur

    class Meta:
        unique_together = ('headword', 'headword_sense_no')

    def __str__(self):
        return f"{self.headword.headword} ({self.headword_sense_no}): {self.meaning}"

    def get_absolute_url(self):
        return reverse('core:update_sense', kwargs={'hw': self.headword.headword, 'sense': self.headword_sense_no})


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


# class Entry(models.Model):
#     class Meta:
#         verbose_name_plural = 'entries'
#
#     GRAMMATICAL_GENDER = '名詞性標記'
#     AGENT_FOCUS = '主事焦點'
#     PATIENT_FOCUS = '受事焦點'
#     LOCATIVE_FOCUS = '處所焦點'
#     REFERENCE_FOCUS = '參考焦點'
#     ZERO_FOCUS = '零焦點標記'
#
#     FOCUS_CHOICES = (
#         (GRAMMATICAL_GENDER, '名詞性標記'),
#         (AGENT_FOCUS, '主事焦點'),
#         (PATIENT_FOCUS, '受事焦點'),
#         (LOCATIVE_FOCUS, '處所焦點'),
#         (REFERENCE_FOCUS, '參考焦點'),
#         (ZERO_FOCUS, '零焦點標記'),
#     )
#
    NOUN = '名詞'
    VERB = '動詞'
    MULTI = '多重詞性'
    OTHER = '其他'
    WORD_CLASS_CHOICES = (
        (NOUN, '名詞'),
        (VERB, '動詞'),
        (MULTI, '多重詞性'),
        (OTHER, '其他'),
    )

#     HAN_BORROWED = '漢語借字'
#     JP_BORROWED = '日語借字'
#     MIN_BORROWED = '閩南語借字'
#     PLANT = '植物'
#     NATURE = '自然'
#     QUANTIFIER = '計量'
#     HUNTING = '狩獵'
#     TEXTILE = '織布服飾'
#     TRANSPORTATION = '交通'
#     RELATIVE = '親屬稱謂'
#     EVERYDAY = '日常生活（含用品）'
#     ANIMAL = '動物'
#     BUILDING = '建築'
#     BODY = '身體'
#     AGRICULTURE = '農耕'
#     RELIGION = '宗教'
#     FOOD = '食物'
#     TAG_CHOICES = (
#         (HAN_BORROWED, '漢語借字'),
#         (JP_BORROWED, '日語借字'),
#         (MIN_BORROWED, '閩南語借字'),
#         (PLANT, '植物'),
#         (NATURE, '自然'),
#         (QUANTIFIER, '計量'),
#         (HUNTING, '狩獵'),
#         (TEXTILE, '織布服飾'),
#         (TRANSPORTATION, '交通'),
#         (RELATIVE, '親屬稱謂'),
#         (EVERYDAY, '日常生活（含用品）'),
#         (ANIMAL, '動物'),
#         (BUILDING, '建築'),
#         (BODY, '身體'),
#         (AGRICULTURE, '農耕'),
#         (RELIGION, '宗教'),
#         (FOOD, '食物'),
#     )
#
#     item_name = models.CharField(max_length=255, unique=True)  # 詞項
#     item_root = models.CharField(max_length=255, blank=True, default="")
#     user = models.CharField(max_length=255, blank=True, default="")
#     created_date = models.DateField(default=datetime.date.today)
#     modified_date = models.DateTimeField(auto_now=True)
#     is_root = models.BooleanField(blank=True, default=False)
#     meaning = models.CharField(max_length=255, blank=True, default="")
#     meaning_en = models.CharField(max_length=255, blank=True, default="")
#     main_meaning_word_class = models.CharField(max_length=255, blank=True, default="")
#     word_class = models.CharField(max_length=255, choices=WORD_CLASS_CHOICES, default=WORD_CLASS_CHOICES[3][0])
#     cultural_notes = models.CharField(max_length=255, blank=True, default="")
#     focus = models.CharField(max_length=255, blank=True, default="", choices=FOCUS_CHOICES)
#     phrase = models.CharField(max_length=255, blank=True, default="")  # 詞組
#     phrase_ch = models.CharField(max_length=255, blank=True, default="")
#     phrase_en = models.CharField(max_length=255, blank=True, default="")
#     char_strokes_first = models.CharField(max_length=255, blank=True, default="")
#     char_strokes_all = models.CharField(max_length=255, blank=True, default="")
#     frequency = models.IntegerField(blank=True, default=0)
#     picture = models.ImageField(upload_to='pictures/', blank=True)
#     sound = models.FileField(upload_to='sound/', blank=True)
#     grammar_notes = models.CharField(max_length=255, blank=True, default="")  # 語法註記
#     refer_to = models.CharField(max_length=255, blank=True, default="")  # 參照
#     tag = MultiSelectField(choices=TAG_CHOICES, default="", null=True, blank=True)  # 標籤
#     toda = models.CharField(max_length=255, blank=True, default="")
#     toda_root = models.CharField(max_length=255, blank=True, default="")  # todar
#     truku = models.CharField(max_length=255, blank=True, default="")
#     truku_root = models.CharField(max_length=255, blank=True, default="")  # trukur
#     variant = models.CharField(max_length=255, blank=True, default="")
#
#     def __str__(self):
#         return self.item_name
#
#     def get_absolute_url(self):
#         return reverse('core:update', kwargs={'pk': self.id})
