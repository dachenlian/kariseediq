import csv
import datetime
from typing import List
import logging

from django.http.request import HttpRequest

from .models import Entry, Example


logger = logging.getLogger(__name__)


def _convert_to_bool(cell):
    return cell.lower() == 'yes'


def _parse_date(str_date):
    try:
        parsed = datetime.datetime.strptime(str_date, '%m/%d/%Y')
    except ValueError as e:
        logger.exception(e)
        return datetime.datetime.min
    else:
        return parsed


def _add_tag(entry: dict, user: str, tag: str) -> list:
    tags = [e.strip() for e in entry.get('tag', '').split(',')]
    if entry['user'] == user and tag not in tags:
        tags.append(tag)
    return tags


def load_into_db(file):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for idx, row in enumerate(reader, 1):
            row = [r.lower().strip().capitalize() for r in row]
            new_entry = dict(zip(header, row))
            if Entry.objects.filter(item_name=new_entry['item_name']).exists():
                logger.warning(f"{new_entry['item_name']} already exists.\n{new_entry}")
                continue

            if not new_entry['frequency']:
                new_entry['frequency'] = 0

            new_entry['created_date'] = _parse_date(new_entry['created_date'])
            new_entry['is_root'] = _convert_to_bool(new_entry['is_root'])
            new_entry['refer_to'] = new_entry.pop('source')
            new_entry['tag'] = _add_tag(new_entry, 'Kcjason2', '植物')

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
            if idx % 500 == 0:
                logger.debug(f'Processed {idx} rows...')


def gen_query_history(request: HttpRequest):
    logger.debug('Generating query history...')
    qs_length = len(request.session.get('queryset'))

    history_list = request.session.get('history_list', [])

    search_name = request.GET.get('search_name', "")
    search_filter = request.GET.get('search_filter', "")
    search_root = request.session.get('search_root', '')

    query_str = f"({qs_length} hits) " \
        f"<strong>Item</strong>: {search_name} | " \
        f"<strong>Filter</strong>: {search_filter} | " \
        f"<strong>Roots</strong>: {search_root}"

    query_dict = {
        'query_str': query_str,
        'queryset': request.session.get('queryset')
    }
    history_list.append(query_dict)
    request.session['history_list'] = history_list
    logger.debug(history_list)
    return request


def get_related(qs: List[dict]) -> list:
    """
    Get data from related models, such as examples.
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
