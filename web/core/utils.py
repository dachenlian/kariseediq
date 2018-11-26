import csv
from .models import Entry
import datetime


def convert_to_boolean(cell):
    return cell.lower() == 'yes'


def load_into_db(file):
    with open(file) as fp:
        reader = csv.reader(fp)
        header = next(reader)

        for row in reader:
            new_entry = dict(zip(header, row))
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
