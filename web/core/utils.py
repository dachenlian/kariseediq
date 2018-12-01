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
logger = logging.getLogger(__name__).addHandler(logging.StreamHandler())


def convert_to_boolean(cell):
    return cell.lower() == 'yes'


def load_into_db(file):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for row in reader:
            new_entry = dict(zip(header, row))
            if Entry.objects.filter(itemName=new_entry['itemName']).count():
                logger.warning(f"{new_entry['itemName']} already exists.\n{new_entry}")
                continue
            new_entry['isRoot'] = convert_to_boolean(new_entry['isRoot'])
            new_entry['isPlant'] = convert_to_boolean(new_entry['isPlant'])
            if not new_entry['occurrence']:
                new_entry['occurrence'] = 0
            try:
                new_entry['time'] = datetime.datetime.strptime(new_entry['time'], '%m/%d/%Y')
            except ValueError as e:
                print(e)
                print(row)
                new_entry['time'] = datetime.datetime.min

            Entry(**new_entry).save()
