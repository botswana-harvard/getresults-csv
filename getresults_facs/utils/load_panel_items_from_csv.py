import csv
import os

from django.conf import settings

from ..models import Panel, Utestid, PanelItem


def load_panel_items_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/panel_items.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        panel = None
        for row in reader:
            r = dict(zip(header, row))
            panel = Panel.objects.get(name=r['panel_name'].strip())
            utestid = Utestid.objects.get(name=r['utestid'].strip())
            try:
                PanelItem.objects.get(panel=panel, utestid=utestid)
            except PanelItem.DoesNotExist:
                PanelItem.objects.create(
                    panel=panel,
                    utestid=utestid,
                    value_type=r['value_type'],
                    value_datatype=r['value_datatype'],
                    lower_limit=r['lower_limit'] if r['lower_limit'] else None,
                    upper_limit=r['upper_limit'] if r['upper_limit'] else None,
                    precision=r['precision'] if r['precision'] else None,
                    formula=r['formula'] if r['formula'] else None,
                )
