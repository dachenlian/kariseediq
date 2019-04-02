import csv
import datetime
import re
import logging
import time
from typing import List

from django.http.request import HttpRequest
from django.forms.models import model_to_dict

from .forms import SenseForm
from .models import Headword, Sense, Phrase, Example

logger = logging.getLogger(__name__)


def _add_tag(entry: dict, user: str, tag: str) -> list:
    tags = [e.strip() for e in entry.get('tag', '').split(',')]
    if entry['user'] == user and tag not in tags:
        tags.append(tag)
    return tags


def _clean_entry(entry: dict) -> dict:
    headword, headword_sense_no = _split_item_name(entry.pop('item_name'))
    root, root_sense_no = _split_item_name(entry.pop('item_root'))

    entry['first_letter'] = first_letter(headword)
    entry['headword'] = headword
    entry['headword_sense_no'] = headword_sense_no
    entry['root'] = root
    entry['root_sense_no'] = root_sense_no
    entry['created_date'] = _parse_date(entry['created_date'])
    entry['refer_to'] = entry.pop('source')
    entry['tag'] = _add_tag(entry, 'Kcjason2', '植物')
    entry['is_root'] = _convert_to_bool(entry.pop('is_root'))

    if not entry['frequency']:
        entry['frequency'] = 0

    return entry


def _contains_digit(s):
    return any(c.isdigit() for c in s)


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


def _split_item_name(s):
    if _contains_digit(s):
        m = re.match(r'([A-Za-z\-\s]+)_?(\d)?', s)
        headword, sense = m.group(1).strip(), m.group(2).strip()
    else:
        headword = s.strip()
        sense = 1
    return headword, sense


def build_autocomplete_response(qs: List[Headword]) -> List[str]:
    """
    Return an enumerated list of senses for a root Headword.
    :param qs: A Headword
    :return:
    """
    return [f'{hw.headword}\n ({idx}) {s.meaning}' for hw in qs for idx, s in enumerate(hw.senses.all(), 1)]


def first_letter(string):
    for s in string:
        if s.isalpha():
            return s


def load_into_db(file="seediq_items_updated.csv"):
    start = time.time()

    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for idx, row in enumerate(reader, 1):
            row = [r.strip() for r in row]
            new_entry = _clean_entry(dict(zip(header, row)))
            headword = new_entry.pop('headword')
            variant = new_entry.pop('variant')
            is_root = new_entry.pop('is_root')
            first_lttr = new_entry.pop('first_letter')

            headword, created = Headword.objects.get_or_create(
                headword=headword,
                defaults={
                    'first_letter': first_lttr,
                    'variant': variant,
                    'is_root': is_root,
                    'user': new_entry.get('user'),
                    'created_date': new_entry.get('created_date')
                }
            )
            if not created:
                logger.debug(f'{headword.headword} already exists. Retrieving from DB.')

            if Sense.objects.filter(headword=headword,
                                    headword_sense_no=new_entry.get('headword_sense_no'),
                                    meaning=new_entry.get('meaning')
                                    ).exists():
                logger.warning(f"{headword} with sense meaning {new_entry.get('meaning')}"
                               f" already exists.")
                continue

            sentence = new_entry.pop('sentence')
            sentence_en = new_entry.pop('sentence_en')
            sentence_ch = new_entry.pop('sentence_ch')

            phrase = new_entry.pop('phrase')
            phrase_ch = new_entry.pop('phrase_ch')
            phrase_en = new_entry.pop('phrase_en')

            sense = Sense.objects.create(headword=headword, **new_entry)

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

    end = time.time()
    logger.debug(f'Completed in {datetime.timedelta(seconds=end - start)}.')


def load_extra_meaning(file='seediq_extra_meaning_updated.csv'):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for idx, row in enumerate(reader, 1):
            row = [r.strip() for r in row]
            new_entry = dict(zip(header, row))
            headword, _ = _split_item_name(new_entry.pop('item_name'))
            meaning = new_entry.pop('meaning')
            meaning_en = new_entry.pop('meaning_en')
            main_meaning_word_class = new_entry.pop('word_class')

            if not meaning and not new_entry['sentence']:
                logger.debug(f'{headword}: Empty row.')
                continue

            headword, created = Headword.objects.get_or_create(
                headword=headword,
                defaults={
                    'first_letter': first_letter(headword)
                }
            )
            if created:
                logger.debug(f'Created headword: {headword}')
            if meaning:
                sense, created = Sense.objects.get_or_create(
                    headword=headword,
                    meaning=meaning,
                    defaults={
                        'headword_sense_no': headword.senses.count() + 1,
                        'main_meaning_word_class': main_meaning_word_class,
                        'meaning_en': meaning_en,
                    }
                )
            else:
                # Only contains extra examples
                sense = headword.senses.first()
            if new_entry['sentence']:
                if sense.examples.filter(sentence=new_entry['sentence']).exists():
                    logger.debug(f"{headword.headword} ({sense.headword_sense_no}) -- {new_entry['sentence']} already exists.")
                    continue
                Example.objects.create(sense=sense, **new_entry)
            if idx % 100 == 0:
                logger.debug(f'Processed {idx}...')


def load_extra_phrases(file='seediq_extra_phrases_updated.csv'):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for idx, row in enumerate(reader, 1):
            row = [r.strip() for r in row]
            new_entry = dict(zip(header, row))
            headword, _ = _split_item_name(new_entry.pop('item_name'))

            if not new_entry['phrase']:
                logger.debug(f'{headword}: empty row.')
                continue
            headword = Headword.objects.get(headword=headword)
            sense = headword.senses.first()
            Phrase.objects.create(sense=sense, **new_entry)


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


def get_related(qs: List[Headword]) -> List[dict]:
    """
    Get data from related models, such as examples and phrases.
    :param qs: A list of Headword objects.
    :return:
    """
    fieldnames = SenseForm.Meta.fields
    results = []
    for headword in qs:
        senses = headword.senses.all().values('id', *fieldnames)
        head_dict = model_to_dict(headword, ('user', 'variant', 'is_root', 'created_date'))
        head_dict['hw_created_date'] = head_dict.pop('created_date')

        for sense in senses:
            sense.update(head_dict)
            sense['headword'] = headword.headword
            sense['tag'] = ",".join(sense['tag'])
            _id = sense.pop('id')

            examples = Example.objects.filter(sense=_id)
            sentence = [f'({i}) {ex.sentence}' for i, ex in enumerate(examples, 1) if ex.sentence]
            sentence_en = [f'({i}) {ex.sentence_en}' for i, ex in enumerate(examples, 1) if ex.sentence_en]
            sentence_ch = [f'({i}) {ex.sentence_ch}' for i, ex in enumerate(examples, 1) if ex.sentence_ch]
            sense['sentence'] = " ".join(sentence)
            sense['sentence_en'] = " ".join(sentence_en)
            sense['sentence_ch'] = " ".join(sentence_ch)

            phrases = Phrase.objects.filter(sense=_id)
            phrase = [f'({i}) {ex.phrase}' for i, ex in enumerate(phrases, 1) if ex.phrase]
            phrase_en = [f'({i}) {ex.phrase_en}' for i, ex in enumerate(phrases, 1) if ex.phrase_en]
            phrase_ch = [f'({i}) {ex.phrase_ch}' for i, ex in enumerate(phrases, 1) if ex.phrase_ch]
            sense['phrase'] = " ".join(phrase)
            sense['phrase_en'] = " ".join(phrase_en)
            sense['phrase_ch'] = " ".join(phrase_ch)

            results.append(sense)
    return results
