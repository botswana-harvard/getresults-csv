import codecs
import csv
import os

from getresults_order.models import Utestid
from decimal import Decimal, InvalidOperation
from getresults_csv.models import CsvFormat, CsvDictionary, CsvField
from getresults_sender.models import SenderModel


class Configure(object):

    def __init__(self, path, utestids_filename=None, csv_formats_filename=None, csv_dictionaries_filename=None):
        self.path = path
        self.utestids_filename = utestids_filename or 'utestids.csv'
        self.csv_formats_filname = csv_formats_filename or 'csv_formats.csv'
        self.csv_dictionaries_filename = csv_dictionaries_filename or 'csv_dictionaries.csv'
        self.load_utestids()
        self.load_csv_formats()
        self.load_csv_dictionaries()

    def load_csv_formats(self, path=None, filename=None):
        path = path or self.path
        filename = filename or self.csv_formats_filname
        with open(os.path.join(path, filename), 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            header_row = next(reader)
            expected_header_row = [
                'name', 'sender_model', 'sample_file', 'delimiter', 'encoding']
            if header_row != expected_header_row:
                raise ValueError(
                    'Cannot import {}. Invalid header row. Expected {}'.format(
                        filename, expected_header_row))
            for row in reader:
                row = dict(zip(header_row, row))
                if row.get('name'):
                    try:
                        CsvFormat.objects.get(name__iexact=row.get('name'))
                    except CsvFormat.DoesNotExist:
                        try:
                            sender_model = SenderModel.objects.get(name=row.get('sender_model'))
                        except SenderModel.DoesNotExist:
                            sender_model = None
                        if row.get('sample_file'):
                            sample_file = os.path.join(path, row.get('sample_file'))
                        else:
                            sample_file = None
                        CsvFormat.objects.create(
                            name=row.get('name'),
                            sender_model=sender_model,
                            sample_file=sample_file,
                            delimiter=codecs.decode(row.get('delimiter').strip() or ',', 'unicode_escape'),
                            encoding=row.get('encoding', 'utf-8')
                        )

    def load_utestids(self, path=None, filename=None):
        """Imports config data from utestid, csv_formats and csv_dictionaries."""
        path = path or self.path
        utestid_filename = filename or self.utestids_filename
        with open(os.path.join(path, utestid_filename), 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            header_row = next(reader)
            expected_header_row = [
                'name', 'description', 'value_type', 'value_datatype', 'lower_limit',
                'upper_limit', 'precision', 'formula', 'formula_utestid_name']
            if header_row != expected_header_row:
                raise ValueError(
                    'Cannot import {}. Invalid header row. Expected {}'.format(
                        filename, expected_header_row))
            for row in reader:
                row = dict(zip(header_row, row))
                if row.get('name'):
                    try:
                        Utestid.objects.get(name__iexact=row.get('name'))
                    except Utestid.DoesNotExist:
                        Utestid.objects.create(
                            name=row.get('name'),
                            description=row.get('description'),
                            value_type=row.get('value_type'),
                            value_datatype=row.get('value_datatype'),
                            lower_limit=self.to_decimal(row.get('lower_limit')),
                            upper_limit=self.to_decimal(row.get('upper_limit')),
                            precision=self.to_int(row.get('precision')),
                            formula=row.get('formula'),
                            formula_utestid_name=row.get('formula_utestid_name'),
                        )

    def load_csv_dictionaries(self, path=None, filename=None):
        path = path or self.path
        filename = filename or self.csv_dictionaries_filename
        with open(os.path.join(path, filename), 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            header_row = next(reader)
            expected_header_row = ['csv_format', 'field_label', 'csv_field']
            if header_row != expected_header_row:
                raise ValueError(
                    'Cannot import {}. Invalid header row. Expected {}'.format(
                        filename, expected_header_row))
            for row in reader:
                row = dict(zip(header_row, row))
                csv_format = CsvFormat.objects.get(name__iexact=row.get('csv_format'))
                csv_field = CsvField.objects.get(name__iexact=row.get('csv_field'), csv_format=csv_format)
                try:
                    CsvDictionary.objects.get(
                        csv_format=csv_format,
                        csv_field=csv_field
                    )
                except CsvDictionary.DoesNotExist:
                    CsvDictionary.objects.create(
                        csv_format=csv_format,
                        field_label=row.get('field_label'),
                        csv_field=csv_field,
                    )

    def to_int(self, value):
        try:
            return int(value)
        except ValueError:
            return None

    def to_decimal(self, value):
        try:
            return Decimal(value)
        except InvalidOperation:
            return None
