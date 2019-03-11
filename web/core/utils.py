import csv
import datetime
from typing import List
import logging

from django.http.request import HttpRequest

from .models import Headword, Sense, Phrase, Example


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


def _clean_entry(entry):

    entry['created_date'] = _parse_date(entry['created_date'])
    entry['refer_to'] = entry.pop('source')
    entry['tag'] = _add_tag(entry, 'Kcjason2', '植物')
    entry['is_root'] = _convert_to_bool(entry.pop('is_root'))

    if not entry['frequency']:
        entry['frequency'] = 0

    return entry


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
            new_entry = _clean_entry(dict(zip(header, row)))
            headword = new_entry.pop('item_name')
            is_root = new_entry.pop('is_root')
            root = new_entry.pop('item_root')

            headword, created = Headword.objects.get_or_create(headword=headword,
                                                               is_root=is_root,
                                                               root=root,
                                                               created_date=new_entry.get('created_date'))
            if Sense.objects.filter(headword=headword, meaning=new_entry.get('meaning')).exists():
                logger.warning(f"{new_entry['item_name']} with sense meaning {new_entry.get('meaning')}"
                               f" already exists.")
                continue

            new_entry['sense_no'] =
            sentence = new_entry.pop('sentence')
            sentence_en = new_entry.pop('sentence_en')
            sentence_ch = new_entry.pop('sentence_ch')

            phrase = new_entry.pop('phrase')
            phrase_ch = new_entry.pop('phrase_ch')
            phrase_en = new_entry.pop('phrase_en')

            sense = Sense.objects.create(**new_entry)

            Example.objects.create(
                sense=sense,
                sentence=sentence,
                sentence_ch=sentence_ch,
                sentence_en=sentence_en,
            )

            Phrase.objects.create(
                sense=sense,
                phrase=phrase,
                phrase_ch=phrase_ch,
                phrase_en=phrase_en,
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
