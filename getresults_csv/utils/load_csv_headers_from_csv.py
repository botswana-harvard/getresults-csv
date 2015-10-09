import csv
import os

from django.conf import settings

from ..models import Header, HeaderItem


def load_csv_headers_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/csv_headers.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header_row = next(reader)
        header_row = [h.lower() for h in header_row]
        for row in reader:
            r = dict(zip(header_row, row))
            try:
                header = Header.objects.get(name=r['header_name'].lower())
            except Header.DoesNotExist:
                header = Header.objects.create(name=r['header_name'].lower())
            try:
                HeaderItem.objects.get(header=header, key=r['key'].lower())
            except HeaderItem.DoesNotExist:
                HeaderItem.objects.create(
                    header=header,
                    key=r['key'].lower(),
                    header_field=r['header_field'].lower()
                )
