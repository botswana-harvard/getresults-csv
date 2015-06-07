import csv
import os

from django.conf import settings

from ..models import Panel, Utestid, PanelItem


def load_panel_items_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/panel_items.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        panel = None
        for row in reader:
            r = dict(zip(header, row))
            panel = Panel.objects.get(name=r['panel_name'].strip().lower())
            utestid = Utestid.objects.get(name=r['utestid'].strip().lower())
            try:
                PanelItem.objects.get(panel=panel, utestid=utestid)
            except PanelItem.DoesNotExist:
                PanelItem.objects.create(
                    panel=panel,
                    utestid=utestid,
                )
