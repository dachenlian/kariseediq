from django.db import models
import datetime
from django.urls import reverse
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User


class Entry(models.Model):
    class Meta:
        verbose_name_plural = 'entries'

    NOUN = 'NOUN'
    VERB = 'VERB'
    MULTI = 'MULTI'
    OTHER = 'OTHER'
    WORDCLASS_CHOICES = (
        (NOUN, '名詞'),
        (VERB, '動詞'),
        (MULTI, '多重詞性'),
        (OTHER, '其他'),
    )

    HAN_BORROWED = 'HAN_BORROWED'
    JP_BORROWED = 'JP_BORROWED'
    MIN_BORROWED = 'MIN_BORROWED'
    PLANT = 'PLANT'
    NATURE = 'NATURE'
    QUANTIFIER = 'QUANTIFIER'
    HUNTING = 'HUNTING'
    TEXTILE = 'TEXTILE'
    TRANSPORTATION = 'TRANSPORTATION'
    RELATIVE = 'RELATIVE'
    EVERYDAY = 'EVERYDAY'
    ANIMAL = 'ANIMAL'
    BUILDING = 'BUILDING'
    BODY = 'BODY'
    AGRICULTURE = 'AGRICULTURE'
    RELIGION = 'RELIGION'
    FOOD = 'FOOD'
    TAGGING_CHOICES = (
        (HAN_BORROWED, '漢語借字'),
        (JP_BORROWED, '日語借字'),
        (MIN_BORROWED, '閩南語借字'),
        (PLANT, '植物'),
        (NATURE, '自然'),
        (QUANTIFIER, '計量'),
        (HUNTING, '狩獵'),
        (TEXTILE, '織布服飾'),
        (TRANSPORTATION, '交通'),
        (RELATIVE, '親屬稱謂'),
        (EVERYDAY, '日常生活（含用品）'),
        (ANIMAL, '動物'),
        (BUILDING, '建築'),
        (BODY, '身體'),
        (AGRICULTURE, '農耕'),
        (RELIGION, '宗教'),
        (FOOD, '食物'),
    )

    item_name = models.CharField(max_length=255, unique=True)  # 詞項
    item_root = models.CharField(max_length=255, blank=True, default="")
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='entries')
    created_date = models.DateField(default=datetime.date.today)
    modified_date = models.DateTimeField(auto_now=True)
    is_root = models.BooleanField(blank=True, default=False)
    meaning = models.CharField(max_length=255, blank=True, default="")
    meaning_en = models.CharField(max_length=255, blank=True, default="")
    main_meaning_word_class = models.CharField(max_length=255, blank=True, default="")
    word_class = MultiSelectField(choices=WORDCLASS_CHOICES, default=NOUN)
    cultural_notes = models.CharField(max_length=255, blank=True, default="")
    focus = models.CharField(max_length=255, blank=True, default="")
    phrase = models.CharField(max_length=255, blank=True, default="")  # 詞組
    phrase_ch = models.CharField(max_length=255, blank=True, default="")
    phrase_en = models.CharField(max_length=255, blank=True, default="")
    char_strokes_first = models.CharField(max_length=255, blank=True, default="")
    char_strokes_all = models.CharField(max_length=255, blank=True, default="")
    frequency = models.IntegerField(blank=True, default=0)
    has_picture = models.BooleanField(default=False)
    grammar_notes = models.CharField(max_length=255, blank=True, default="")  # 語法註記
    sentence = models.TextField(blank=True, default="")
    sentence_ch = models.TextField(blank=True, default="")
    sentence_en = models.TextField(blank=True, default="")
    source = models.CharField(max_length=255, blank=True, default="")  # 參照
    tag = MultiSelectField(choices=TAGGING_CHOICES, default=NATURE)  # 標籤
    toda = models.CharField(max_length=255, blank=True, default="")
    toda_root = models.CharField(max_length=255, blank=True, default="")  # todar
    truku = models.CharField(max_length=255, blank=True, default="")
    truku_root = models.CharField(max_length=255, blank=True, default="")  # trukur
    variant = models.CharField(max_length=255, blank=True, default="")

    def __str__(self):
        return self.item_name

    def get_absolute_url(self):
        return reverse('core:update', kwargs={'pk': self.id})


