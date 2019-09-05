import csv
import datetime
import re
import logging
import time
from typing import List, Tuple

from cihai.core import Cihai
from django.http.request import HttpRequest
from django.forms.models import model_to_dict
from django.db import IntegrityError

from .forms import SenseForm
from .models import Headword, Sense, Phrase, Example

logger = logging.getLogger(__name__)

C = Cihai()
if not C.unihan.is_bootstrapped:
    C.unihan.bootstrap()


def _add_tag(entry: dict, user: str, tag: str) -> list:
    tags = [e.strip() for e in entry.get('tag', '').split(',')]
    if entry['user'] == user and tag not in tags:
        tags.append(tag)
    return tags


def _clean_entry(entry: dict) -> dict:
    headword, headword_sense_no = _split_item_name(entry.pop('item_name'))
    root, root_sense_no = _split_item_name(entry.pop('item_root'))
    char_strokes_first, char_strokes_all = get_char_strokes(entry['meaning'])

    entry['char_strokes_first'] = char_strokes_first
    entry['char_strokes_all'] = char_strokes_all
    entry['only_letters'] = only_letters(headword)
    entry['headword'] = headword
    entry['headword_sense_no'] = headword_sense_no
    entry['root'] = root
    entry['word_class']: list = entry.pop('word_class').split()
    entry['focus']: list = entry.pop('focus').split()
    entry['root_sense_no'] = root_sense_no
    entry['created_date'] = _parse_date(entry['created_date'])
    entry['refer_to'] = entry.pop('source')
    entry['tag']: list = _add_tag(entry, 'Kcjason2', '植物')
    entry['is_root'] = _convert_to_bool(entry.pop('is_root'))
    entry['variant'] = [e.strip() for e in entry.pop('variant').split(';')]
    del entry['toda_root']
    del entry['truku_root']

    if not entry['frequency']:
        entry['frequency'] = 0

    return entry


def _contains_digit(s):
    return any(c.isdigit() for c in s)


def _convert_to_bool(cell):
    return cell.lower() == 'yes'


def _parse_date(str_date):
    try:
        parsed = datetime.datetime.strptime(str_date, '%Y-%m-%d')
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


def get_char_strokes(s: str) -> Tuple[str, str]:
    all_char_strokes = []
    for char in s:
        query = C.unihan.lookup_char(char)
        glyph = query.first()
        if glyph:
            strokes = glyph.kTotalStrokes
            all_char_strokes.append(f"{char}/{strokes}")
    if not all_char_strokes:
        return "", ""
    first_char_stroke = all_char_strokes[0]
    all_char_strokes = ",".join(all_char_strokes)
    return first_char_stroke, all_char_strokes


def build_autocomplete_response(qs: List[Headword]) -> List[str]:
    """
    Return an enumerated list of senses for a root Headword.
    :param qs: A Headword
    :return:
    """
    return [f'{hw.headword}\n ({idx}) {s.meaning}' for hw in qs for idx, s in enumerate(hw.senses.all(), 1)]


def only_letters(string):
    return "".join(char for char in string if char.isalpha() or char == ' ')


def load_items(file="../seediq_items_updated-20190726-sung.csv"):
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
            only_lttrs = new_entry.pop('only_letters')

            headword, created = Headword.objects.get_or_create(
                headword=headword,
                # is_root=is_root,
                defaults={
                    'only_letters': only_lttrs,
                    'variant': variant,
                    'is_root': is_root,
                    'user': new_entry.get('user'),
                    'created_date': new_entry.get('created_date')
                }
            )
            if not created:
                logger.debug(f'{headword.headword} already exists. Retrieving from DB.')

            if Sense.objects.filter(headword=headword,
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

            try:
                sense = Sense.objects.create(headword=headword, **new_entry)
            except IntegrityError as e:
                # Possibly caused by an extra space in item name that was eventually stripped during pre-processing.
                logger.error(e, headword.headword, new_entry)
                new_entry['headword_sense_no'] = headword.senses.count() + 1
                sense = Sense.objects.create(headword=headword, **new_entry)

            if sentence:
                Example.objects.create(
                    sense=sense,
                    sentence=sentence,
                    sentence_ch=sentence_ch,
                    sentence_en=sentence_en,
                )

            if phrase:
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


def load_extra_meaning(file='../seediq_extra_meaning_updated-20190726-sung.csv'):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for idx, row in enumerate(reader, 1):
            row = [r.strip() for r in row]
            new_entry = dict(zip(header, row))
            headword, headword_sense_no = _split_item_name(new_entry.pop('item_name'))
            meaning = new_entry.pop('meaning')
            char_strokes_first, char_strokes_all = get_char_strokes(meaning)
            meaning_en = new_entry.pop('meaning_en')
            is_root = new_entry.pop('is_root') == 'yes'
            item_root = new_entry.pop('item_root')
            word_class = new_entry.pop('word_class').split()

            if not meaning and not new_entry['sentence']:
                logger.debug(f'{headword}: Empty row.')
                continue

            headword, created = Headword.objects.get_or_create(
                headword=headword,
                # is_root=is_root,
                defaults={
                    'only_letters': only_letters(headword)
                }
            )
            if created:
                logger.debug(f'Created headword: {headword}')

            sense, created = Sense.objects.get_or_create(
                headword=headword,
                meaning=meaning,
                defaults={
                    'headword_sense_no': headword.senses.count() + 1,
                    'char_strokes_first': char_strokes_first,
                    'char_strokes_all': char_strokes_all,
                    'word_class': word_class,
                    'meaning_en': meaning_en,
                    'root': item_root,
                }
            )

            if new_entry['sentence']:
                if sense.examples.filter(sentence=new_entry['sentence']).exists():
                    logger.debug(f"{headword.headword} ({sense.headword_sense_no}) -- {new_entry['sentence']} already exists.")
                    continue
                Example.objects.create(sense=sense, **new_entry)
            if idx % 100 == 0:
                logger.debug(f'Processed {idx}...')


def load_extra_phrases(file='../seediq_extra_phrases_updated-20190617-sung.csv'):
    """Assuming all phrases relate to the first large items.csv"""
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for idx, row in enumerate(reader, 1):
            row = [r.strip() for r in row]
            new_entry = dict(zip(header, row))
            headword, _ = _split_item_name(new_entry.pop('item_name'))
            meaning = new_entry.pop('meaning')

            if not new_entry['phrase']:
                logger.debug(f'{headword}: empty row.')
                continue
            headword = Headword.objects.get(headword=headword)
            if not Sense.objects.filter(headword=headword, meaning=meaning).exists():
                logger.debug("Sense does not exist:", headword, meaning)
                continue
            sense = headword.senses.get(meaning=meaning)
            # try:
            #     sense = headword.senses.get(meaning=meaning)
            # except Sense.DoesNotExist as e:
            #     logger.debug("DoesNotExist:", headword, meaning)
            #     continue
            Phrase.objects.create(sense=sense, **new_entry)


def load():
    logger.debug('Starting load_items()')
    load_items()
    logger.debug('Starting load_extra_meaning()')
    load_extra_meaning()
    logger.debug('Starting load_extra_phrases()')
    load_extra_phrases()


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
