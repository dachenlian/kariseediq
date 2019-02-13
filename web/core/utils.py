import csv
import datetime
from typing import List
import logging

from django.http.request import HttpRequest

from .models import Entry, Example


logger = logging.getLogger(__name__)


def convert_to_boolean(cell):
    return cell.lower() == 'yes'


# def convert_tags(tags):
#     if not tags:
#         return None
#     split = (t.strip() for t in re.split(r'[，,、]', tags))
#     return ",".join(converted)


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


def get_related(qs: List[dict]) -> list:
    """
    Get data from related models.
    :param qs:
    :return:
    """
    for entry in qs:
        _id = entry.pop('id')
        examples = Example.objects.filter(entry=_id)
        sentence = [f'({i}) {ex.sentence}' for i, ex in enumerate(examples, 1)]
        sentence_en = [f'({i}) {ex.sentence_en}' for i, ex in enumerate(examples, 1)]
        sentence_ch = [f'({i}) {ex.sentence_ch}' for i, ex in enumerate(examples, 1)]

        entry['sentence'] = " ".join(sentence)
        entry['sentence_en'] = " ".join(sentence_en)
        entry['sentence_ch'] = " ".join(sentence_ch)

    return qs
