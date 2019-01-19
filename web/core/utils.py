import csv
import datetime
import logging
import re

from django.http.request import HttpRequest

from .models import Entry, Example


logger = logging.getLogger(__name__)


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
            row = [r.lower().strip() for r in row]
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

            try:
                new_entry['created_date'] = datetime.datetime.strptime(new_entry['created_date'], '%m/%d/%Y')
            except ValueError as e:
                logger.exception(e)
                new_entry['created_date'] = datetime.datetime.min

            new_entry['is_root'] = convert_to_boolean(new_entry['is_root'])

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


def gen_query_history(request: HttpRequest, qs_length: int):
    logger.debug('Generating query history...')
    history = request.session.get('query_history', "").split('<br>')
    search_name = request.GET.get('search_name', "")
    search_filter = request.GET.get('search_filter', "")
    search_root = request.session.get('search_root', False)

    query_str = f"{len(history)}. ({qs_length} hits) " \
        f"<strong>Item</strong>: {search_name} | " \
        f"<strong>filter</strong>: {search_filter} | " \
        f"<strong>Only roots</strong>: {search_root}"
    history.append(query_str)
    request.session['query_history'] = "<br>".join(history)
    logger.debug(history)
    return request

