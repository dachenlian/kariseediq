import csv
import datetime
import logging
import re

from .models import Entry, Example


logger = logging.getLogger()


def convert_to_boolean(cell):
    return cell.lower() == 'yes'


TAG_DICT = dict((y, x) for x, y in Entry.TAG_CHOICES)
WORD_CLASS_DICT = dict((y, x) for x, y in Entry.WORD_CLASS_CHOICES)
FOCUS_DICT = dict((y, x) for x, y in Entry.FOCUS_CHOICES)


def convert_tags(tags):
    if not tags:
        return None
    split = (t.strip() for t in re.split(r'[，,、]', tags))
    converted = (TAG_DICT.get(t) for t in split if t in TAG_DICT)
    return ",".join(converted)


def convert_focus(focus):
    if not focus:
        return ""
    return FOCUS_DICT.get(focus)


def load_into_db(file):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for row in reader:
            new_entry = dict(zip(header, row))
            if Entry.objects.filter(item_name=new_entry['item_name']).count():
                logger.warning(f"{new_entry['item_name']} already exists.\n{new_entry}")
                continue

            new_entry['word_class'] = WORD_CLASS_DICT.get(new_entry['word_class'].strip(), WORD_CLASS_DICT['其他'])
            try:
                new_entry['tag'] = convert_tags(new_entry['tag'])
            except TypeError as e:
                logger.exception(e)
                break

            try:
                new_entry['focus'] = convert_focus(new_entry['focus'])
            except TypeError as e:
                logger.exception(e)
                break

            if not new_entry['frequency']:
                new_entry['frequency'] = 0

            new_entry['is_root'] = new_entry['is_root'].lower() == 'yes'
            new_entry['has_picture'] = new_entry['has_picture'] == 1

            try:
                new_entry['created_date'] = datetime.datetime.strptime(new_entry['created_date'], '%m/%d/%Y')
            except ValueError as e:
                logger.exception(e)
                new_entry['created_date'] = datetime.datetime.min

            sentence = new_entry.pop('sentence')
            sentence_en = new_entry.pop('sentence_en')
            sentence_ch = new_entry.pop('sentence_ch')

            entry = Entry.objects.create(**new_entry)

            Example.objects.create(
                entry=entry,
                sentence=sentence,
                sentence_ch=sentence_ch,
                sentence_en=sentence_en,
            )

