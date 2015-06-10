import sys

from django.core.management.base import BaseCommand, CommandError


from getresults_csv.utils import load_csvmapping_from_csv, load_csv_headers_from_csv, load_csv_file


class Command(BaseCommand):
    help = 'Load data from a folder containing panel.csv and csv_headers.csv'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        for path in options['path']:
            files = []
            files.append(('panels.csv', load_csvmapping_from_csv))
            files.append(('csv_headers.csv', load_csv_headers_from_csv))
            try:
                load_csv_file(path, files)
            except (FileNotFoundError, ) as e:
                sys.stdout.write('\n')
                raise CommandError(e)
