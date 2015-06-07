import csv
import os

from django.conf import settings

from ..models import Utestid


def load_utestids_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/utestids.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        for row in reader:
            r = dict(zip(header, row))
            try:
                Utestid.objects.get(name=r['name'].strip().lower())
            except Utestid.DoesNotExist:
                Utestid.objects.create(
                    name=r['name'].strip().lower(),
                    description=r['description'].strip().lower(),
                    value_type=r['value_type'].lower(),
                    value_datatype=r['value_datatype'].lower(),
                    lower_limit=r['lower_limit'] if r['lower_limit'] else None,
                    upper_limit=r['upper_limit'] if r['upper_limit'] else None,
                    precision=r['precision'] if r['precision'] else None,
                    formula=r['formula'] if r['formula'] else None,
                    formula_utestid=r['formula_utestid'].lower() if r['formula_utestid'] else None,
                )
