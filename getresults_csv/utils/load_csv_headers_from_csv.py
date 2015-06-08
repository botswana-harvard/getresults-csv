import csv
import os

from django.conf import settings

from ..models import CsvHeader, CsvHeaderItem


def load_csv_headers_from_csv(csv_filename=None):
    csv_filename = csv_filename or os.path.join(settings.BASE_DIR, 'testdata/csv_headers.csv')
    with open(csv_filename, 'r') as f:
        reader = csv.reader(f, quotechar="'")
        header = next(reader)
        header = [h.lower() for h in header]
        for row in reader:
            r = dict(zip(header, row))
            try:
                csv_header = CsvHeader.objects.get(name=r['header_name'].lower())
            except CsvHeader.DoesNotExist:
                csv_header = CsvHeader.objects.create(name=r['header_name'].lower())
            try:
                CsvHeaderItem.objects.get(csv_header=csv_header, key=r['key'].lower())
            except CsvHeaderItem.DoesNotExist:
                CsvHeaderItem.objects.create(
                    csv_header=csv_header,
                    key=r['key'].lower(),
                    header_field=r['header_field'].lower()
                )
