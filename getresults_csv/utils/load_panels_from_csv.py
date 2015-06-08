import csv
import os

from django.conf import settings

from ..models import Panel, PanelMapping


def load_panels_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/panels.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        panel = None
        for row in reader:
            r = dict(zip(header, row))
            try:
                panel = Panel.objects.get(name=r['panel'].strip().lower())
            except Panel.DoesNotExist:
                panel = Panel.objects.create(name=r['panel'].strip().lower())
            try:
                PanelMapping.objects.get(
                    panel=panel,
                    csv_field_name=r['csv_field'].strip().lower())
            except PanelMapping.DoesNotExist:
                PanelMapping.objects.create(
                    panel=panel,
                    csv_field_name=r['csv_field'].strip().lower(),
                    utestid_name=r['utestid'].strip().lower())
