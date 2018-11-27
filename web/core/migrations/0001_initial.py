# Generated by Django 2.1.3 on 2018-11-26 15:48

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('book', models.CharField(blank=True, default='', max_length=255)),
                ('cIndex', models.CharField(blank=True, default='', max_length=255)),
                ('creator', models.CharField(blank=True, default='', max_length=255)),
                ('culture', models.CharField(blank=True, default='', max_length=255)),
                ('dialect', models.CharField(blank=True, default='', max_length=255)),
                ('dialectNum', models.CharField(blank=True, default='', max_length=255)),
                ('focus', models.CharField(blank=True, default='', max_length=255)),
                ('hasBranch', models.CharField(blank=True, default='', max_length=255)),
                ('idom', models.CharField(blank=True, default='', max_length=255)),
                ('idomCh', models.CharField(blank=True, default='', max_length=255)),
                ('idomEn', models.CharField(blank=True, default='', max_length=255)),
                ('indexPrefix', models.CharField(blank=True, default='', max_length=255)),
                ('isPlant', models.BooleanField(blank=True, default=False)),
                ('isRoot', models.BooleanField(blank=True, default=False)),
                ('itemId', models.CharField(blank=True, default='', max_length=255)),
                ('itemName', models.CharField(max_length=255)),
                ('mainMeaningWordclass', models.CharField(blank=True, default='', max_length=255)),
                ('detail', models.CharField(blank=True, default='', max_length=255)),
                ('meaning', models.CharField(blank=True, default='', max_length=255)),
                ('meaningEn', models.CharField(blank=True, default='', max_length=255)),
                ('notSure', models.CharField(blank=True, default='', max_length=255)),
                ('occurrence', models.IntegerField(blank=True, default=0)),
                ('period', models.CharField(blank=True, default='', max_length=255)),
                ('picture', models.CharField(blank=True, default='', max_length=255)),
                ('question', models.CharField(blank=True, default='', max_length=255)),
                ('remark', models.CharField(blank=True, default='', max_length=255)),
                ('sentence', models.TextField(blank=True, default='')),
                ('sentenceCh', models.TextField(blank=True, default='')),
                ('sentenceEn', models.TextField(blank=True, default='')),
                ('sound', models.CharField(blank=True, default='', max_length=255)),
                ('source', models.CharField(blank=True, default='', max_length=255)),
                ('tagging', models.CharField(blank=True, choices=[('HAN_BORROWED', '漢語借字'), ('JP_BORROWED', '日語借字'), ('MIN_BORROWED', '閩南語借字'), ('PLANT', '植物'), ('NATURE', '自然'), ('QUANTIFIER', '計量'), ('HUNTING', '狩獵'), ('TEXTILE', '織布服飾'), ('TRANSPORTATION', '交通'), ('RELATIVE', '親屬稱謂'), ('EVERYDAY', '日常生活（含用品）'), ('ANIMAL', '動物'), ('BUILDING', '建築'), ('BODY', '身體'), ('AGRICULTURE', '農耕'), ('RELIGION', '宗教'), ('FOOD', '食物')], default='NATURE', max_length=255)),
                ('time', models.DateField(blank=True, default=datetime.date.today, null=True)),
                ('toda', models.CharField(blank=True, default='', max_length=255)),
                ('todar', models.CharField(blank=True, default='', max_length=255)),
                ('truku', models.CharField(blank=True, default='', max_length=255)),
                ('trukur', models.CharField(blank=True, default='', max_length=255)),
                ('ucode', models.CharField(blank=True, default='', max_length=255)),
                ('variant', models.CharField(blank=True, default='', max_length=255)),
                ('wordClass', models.CharField(blank=True, choices=[('NOUN', '名詞'), ('VERB', '動詞'), ('MULTI', '多重詞性')], default='NOUN', max_length=255)),
                ('wordRoot', models.CharField(blank=True, default='', max_length=255)),
            ],
        ),
    ]
