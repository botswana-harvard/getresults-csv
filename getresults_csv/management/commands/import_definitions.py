import os
import sys

from unipath import Path
from collections import OrderedDict

from django.core.management.base import BaseCommand, CommandError

from getresults.utils import load_panels_from_csv, load_utestids_from_csv, load_panel_items_from_csv

from getresults_csv.utils import load_csvmapping_from_csv, load_csv_headers_from_csv


class Command(BaseCommand):
    help = 'Import data from a folder containing panels.csv, utestids.csv, panel_items.csv and csv_headers.csv'

    def add_arguments(self, parser):
        parser.add_argument('path', nargs='+', type=str)

    def handle(self, *args, **options):
        for path in options['path']:
            try:
                path = Path(os.path.expanduser(path))
                files = []
                files.append(('panels.csv', load_panels_from_csv))
                files.append(('panels.csv', load_csvmapping_from_csv))
                files.append(('utestids.csv', load_utestids_from_csv))
                files.append(('panel_items.csv', load_panel_items_from_csv))
                files.append(('csv_headers.csv', load_csv_headers_from_csv))
                sys.stdout.write('Importing from {}...\n'.format(str(path)))
                for filename, load_func in files:
                    try:
                        sys.stdout.write('    {}'.format(filename))
                        load_func(os.path.join(path, filename))
                        sys.stdout.write('. OK\n')
                    except (FileNotFoundError, ) as e:
                        sys.stdout.write('. ERROR {}\n'.format(str(e)))
                sys.stdout.write('Done.\n'.format(str(path)))
            except (FileNotFoundError, ) as e:
                sys.stdout.write('\n')
                raise CommandError(e)
