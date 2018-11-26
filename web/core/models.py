from django.db import models
import datetime


class Entry(models.Model):
    NOUN = 'NOUN'
    VERB = 'VERB'
    MULTI = 'MULTI'
    OTHER = 'OTHER'
    WORDCLASS_CHOICES = (
        (NOUN, '名詞'),
        (VERB, '動詞'),
        (MULTI, '多重詞性'),
        ()
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

    book = models.CharField(blank=True, default="")
    cIndex = models.CharField(blank=True, default="")
    creator = models.CharField(blank=True, default="")
    culture = models.CharField(blank=True, default="")
    dialectNum = models.CharField(blank=True, default="")
    focus = models.CharField(blank=True, default="")
    hasBranch = models.CharField(blank=True, default="")
    idom = models.CharField(blank=True, default="")
    idomCh = models.CharField(blank=True, default="")
    idomEn = models.CharField(blank=True, default="")
    indexPrefix = models.CharField(blank=True, default="")
    isPlant = models.BooleanField(blank=True, default=False)
    isRoot = models.BooleanField(blank=True, default=False)
    itemId = models.IntegerField(blank=True, default=0)
    itemName = models.CharField()
    mainMeaningWordclass = models.CharField(blank=True, default="")
    meaning = models.CharField(blank=True, default="")
    meaningEn = models.CharField(blank=True, default="")
    notSure = models.CharField(blank=True, default="")
    occurrence = models.IntegerField(blank=True, default=0)
    period = models.CharField(blank=True, default="")
    picture = models.CharField(blank=True, default="")
    question = models.CharField(blank=True, default="")
    remark = models.CharField(blank=True, default="")
    sentence = models.TextField(blank=True, default="")
    sentenceCh = models.TextField(blank=True, default="")
    sentenceEn = models.TextField(blank=True, default="")
    sound = models.CharField(blank=True, default="")
    source = models.CharField(blank=True, default="")
    tagging = models.CharField(blank=True, choices=TAGGING_CHOICES, default=NATURE)
    time = models.DateField(default=datetime.date.today)
    toda = models.CharField(blank=True, default="")
    todar = models.CharField(blank=True, default="")
    truku = models.CharField(blank=True, default="")
    trukur = models.CharField(blank=True, default="")
    ucode = models.CharField(blank=True, default="")
    variant = models.CharField(blank=True, default="")
    wordclass = models.CharField(blank=True, choices=WORDCLASS_CHOICES, default=NOUN)
    wordRoot = models.CharField(blank=True, default="")

