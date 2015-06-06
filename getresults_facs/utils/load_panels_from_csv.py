import csv
import os

from django.conf import settings

from ..models import Panel, PanelMapping


def load_panels_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/panels.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        panel = None
        for row in reader:
            r = dict(zip(header, row))
            try:
                panel = Panel.objects.get(name=r['panel'].strip())
            except Panel.DoesNotExist:
                panel = Panel.objects.create(name=r['panel'].strip())
            PanelMapping.objects.create(
                panel=panel, csv_field=r['csv_field'].strip(), utestid=r['utestid'].strip())
