import csv
import os

from django.conf import settings

from getresults_order.models import Utestid
from getresults_sender.models import SenderPanel
from ..models import CsvDefinition


def load_csv_definitions_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/csv_definitions.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        for row in reader:
            r = dict(zip(header, row))
            sender_panel = SenderPanel.objects.get(name=r['sender_panel'].strip())
            try:
                CsvDefinition.objects.get(
                    sender_panel=sender_panel,
                    field_name=r['field_name'].strip())
            except CsvDefinition.DoesNotExist:
                utestid = Utestid.objects.get(name=r['utestid'].strip())
                CsvDefinition.objects.create(
                    sender_panel=sender_panel,
                    field_name=r['field_name'].strip(),
                    utestid=utestid)
