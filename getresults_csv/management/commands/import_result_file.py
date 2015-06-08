import os
import sys

from unipath import Path

from django.core.management.base import BaseCommand, CommandError

from getresults_csv.getresults import GetResults
from getresults_csv.models import Panel, CsvHeader


class Command(BaseCommand):
    help = 'Import data from a result file'

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1, type=str)
        parser.add_argument(
            '--csv_header_name',
            default='multiset',
            action='store',
            dest='csv_header_name',
            nargs=1,
            help='specify csv header type (default: multiset)')
        parser.add_argument(
            '--delimiter',
            default='\t',
            action='store',
            dest='delimiter',
            nargs=1,
            help='specify delimiter (default: \t)')

    def handle(self, *args, **options):
        try:
            for filename in options['filename']:
                filename = Path(os.path.expanduser(filename))
                sys.stdout.write('Importing {} ...'.format(filename.name))
                getresults = GetResults(
                    filename,
                    csv_header_name=options['csv_header_name'],
                    delimiter=options['delimiter'])
                getresults.save()
                sys.stdout.write('\nDone\n'.format(filename.name))
        except (Panel.DoesNotExist, CsvHeader.DoesNotExist, FileNotFoundError) as e:
            raise CommandError(e)
