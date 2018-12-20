import csv
import datetime
import logging
from web.settings import BASE_DIR
import os
import re

from .models import Entry, Example


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)-12s] [%(levelname)-8s] %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=os.path.join(BASE_DIR, 'debug.log'),
                    filemode='w'
                    )

logger = logging.getLogger(__name__)


def convert_to_boolean(cell):
    return cell.lower() == 'yes'


TAG_DICT = dict((y, x) for x, y in Entry.TAG_CHOICES)
WORD_CLASS_DICT = dict((y, x) for x, y in Entry.WORD_CLASS_CHOICES)


def convert_tags(tags):
    if not tags:
        return None
    split = (t.strip() for t in re.split(r'[，,、]', tags))
    converted = (TAG_DICT.get(t) for t in split if t in TAG_DICT)
    return ",".join(converted)


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
                print(f'{e}:, {new_entry}')
                break

            if not new_entry['frequency']:
                new_entry['frequency'] = 0

            if new_entry['is_root'].lower() == 'yes':
                new_entry['is_root'] = True
            else:
                new_entry['is_root'] = False

            if new_entry['has_picture'] == 1:
                new_entry['has_picture'] = True
            else:
                new_entry['has_picture'] = False
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

