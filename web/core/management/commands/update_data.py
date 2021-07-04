from pathlib import Path

from django.core.management.base import BaseCommand
import pandas as pd
from openpyxl import load_workbook

from core.utils import load
from core.models import Headword




class Command(BaseCommand):
    help = 'Deletes old data and loads new data from CSV'

    def add_arguments(self, parser):
        path = Path('../')
        items_path = list(path.glob('seediq_items_updated_combined*'))[0]
        # items_path = list(path.glob('seediq_items_updated-*'))[0]
        extra_meaning_path = list(path.glob('seediq_extra_meaning_*'))[0]
        extra_phrases_path = list(path.glob('seediq_extra_phrases_*'))[0]

        for p in [items_path, extra_meaning_path, extra_phrases_path]:
            if p.suffix != '.csv':
                self.convert_to_csv(p)

        parser.add_argument('--items', type=Path, default=items_path)
        parser.add_argument('--meaning', type=Path, default=extra_meaning_path)
        parser.add_argument('--phrases', type=Path, default=extra_phrases_path)

    def handle(self, *args, **options):
        Headword.objects.all().delete()

        self.stdout.write("Deleted Headwords!")
        self.stdout.write("Loading new data...")
        # load(items_path=options['items'], extra_meaning_path=options['meaning'], extra_phrases_path=options['phrases'])
        load(items_path=options['items'], combined_file=True, extra_phrases_path=options['phrases'])
        self.stdout.write("Done!")

    def convert_to_csv(self, path: Path) -> None:
        wb = load_workbook(path)
        df = pd.DataFrame(wb.active.values)

        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header

        df.to_csv(path.with_suffix('csv'), index=False)

        self.stdout.write(f'Converted .xlsx to .csv: {path.with_suffix("csv")}')

# if __name__ == '__main__':
#     args = parse_args()
#     load(items_path=args.items, extra_meaning_path=args.meaning, extra_meaning_path=args.phrases)

