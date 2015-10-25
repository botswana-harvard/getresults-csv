import codecs
import csv
import os

from decimal import Decimal, InvalidOperation
from django.conf import settings
from getresults_order.models import Utestid
from getresults_csv.models import CsvFormat, CsvDictionary, CsvField
from getresults_sender.models import SenderModel


class Configure(object):

    """A class to import descriptive/meta data about csv result files.

    Looks for three specifically formatted files:
        * utestids.csv: sender utestids for the Utestid model to be referred to in
          model CsvDictionary
        * csv_format.csv: named file formats. The sample_file should be specified so
          that csv_fields are created.
        * csv_dictionaries.csv: links the csv_format, it's csv_fields to field labels.
          Field labels will be converted to either utestids or "processing field" name.
    """
    def __init__(self, csv_formats_filename=None, csv_dictionaries_filename=None, import_path=None, load=None):
        load = True if load is None else load
        self.import_path = import_path or os.path.join(settings.BASE_DIR, 'testdata')
        self.csv_formats_filename = (
            csv_formats_filename or os.path.join(settings.BASE_DIR, 'testdata/csv_formats.csv'))
        self.csv_dictionaries_filename = (
            csv_dictionaries_filename or os.path.join(settings.BASE_DIR, 'testdata/csv_dictionaries.csv'))
        self.utestids_header_row = [
            'name', 'description', 'value_type', 'value_datatype', 'lower_limit',
            'upper_limit', 'precision', 'formula', 'formula_utestid_name']
        self.csv_formats_header_row = [
            'name', 'sender_model', 'sample_file', 'delimiter', 'encoding']
        self.csv_dictionaries_header_row = ['csv_format', 'field_label', 'csv_field']
        if load:
            self.load_all()

    def load_all(self):
        """Loads all three files in the correct order."""
        self.load_one(
            filename=self.csv_formats_filename,
            header_row=self.csv_formats_header_row,
            create_func=self.create_csv_format)
        self.load_one(
            filename=self.csv_dictionaries_filename,
            header_row=self.csv_dictionaries_header_row,
            create_func=self.create_csv_dictionary)

    def load_one(self, filename, header_row, create_func):
        """Loads one file, confirms header row and creates using create_func if
        the instance does not already exist."""
        with open(filename, 'r', encoding='utf-8', newline='') as f:
            reader = csv.reader(f, delimiter=',')
            csv_header_row = next(reader)
            self.match_header_row_or_raise(csv_header_row, header_row, filename)
            for row in reader:
                row = dict(zip(header_row, row))
                create_func(row)

    def create_utestid(self, row):
        """Creates a utestid instance if one does not already exist."""
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

    def create_csv_dictionary(self, row):
        """Creates a csv_dictionary instance if one does not already exist.

        Note: the csv_formats and utestids must already exist before this method is called."""
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

    def create_csv_format(self, row):
        """Creates a csv_format instance if one does not already exist.

        The csv_format csv must specify a sample_file for the CsvField model to be
        updated. CsvDictionary will refer to CsvField on create."""
        if row.get('name'):
            try:
                CsvFormat.objects.get(name__iexact=row.get('name'))
            except CsvFormat.DoesNotExist:
                try:
                    sender_model = SenderModel.objects.get(name=row.get('sender_model'))
                except SenderModel.DoesNotExist:
                    sender_model = None
                if row.get('sample_file'):
                    sample_file = os.path.join(self.import_path, row.get('sample_file'))
                else:
                    sample_file = None
                CsvFormat.objects.create(
                    name=row.get('name'),
                    sender_model=sender_model,
                    sample_file=sample_file,
                    delimiter=codecs.decode(row.get('delimiter').strip() or ',', 'unicode_escape'),
                    encoding=row.get('encoding', 'utf-8')
                )

    def match_header_row_or_raise(self, row, expected_row, filename):
        """Matches row to expected_row and raises on mismatch."""
        if row != expected_row:
            raise ValueError(
                'Cannot import {}. Invalid header row. Expected {}'.format(
                    filename, expected_row))

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
