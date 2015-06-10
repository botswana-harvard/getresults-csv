import csv
import os

from django.conf import settings

from getresults.models import Panel

from ..models import CsvMapping


def load_csvmapping_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/panels.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        for row in reader:
            r = dict(zip(header, row))
            panel = Panel.objects.get(name=r['panel'].strip().lower())
            try:
                CsvMapping.objects.get(
                    panel=panel,
                    csv_field_name=r['csv_field'].strip().lower())
            except CsvMapping.DoesNotExist:
                CsvMapping.objects.create(
                    panel=panel,
                    csv_field_name=r['csv_field'].strip().lower(),
                    utestid_name=r['utestid'].strip().lower())
