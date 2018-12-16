import csv
import datetime
import logging
from web.settings import BASE_DIR
import os

from .models import Entry


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s [%(name)-12s] [%(levelname)-8s] %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=os.path.join(BASE_DIR, 'debug.log'),
                    filemode='w'
                    )

logger = logging.getLogger(__name__)


def convert_to_boolean(cell):
    return cell.lower() == 'yes'


def load_into_db(file):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for row in reader:
            new_entry = dict(zip(header, row))
            if Entry.objects.filter(item_name=new_entry['item_name']).count():
                logger.warning(f"{new_entry['item_name']} already exists.\n{new_entry}")
                continue

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
                print(e)
                print(row)
                new_entry['created_date'] = datetime.datetime.min

            Entry(**new_entry).save()
