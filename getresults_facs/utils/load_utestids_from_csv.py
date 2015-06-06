import csv
import os

from django.conf import settings

from ..models import Utestid


def load_utestids_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/utestids.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        for row in reader:
            r = dict(zip(header, row))
            try:
                Utestid.objects.get(name=r['name'].strip())
            except Utestid.DoesNotExist:
                Utestid.objects.create(
                    name=r['name'].strip(),
                    quantifier=r['quantifier'].strip(),
                    description=r['description'].strip(),
                )
