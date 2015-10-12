import csv
import os
import re

from collections import OrderedDict
from dateutil.parser import parse
from decimal import Decimal, InvalidOperation

from .models import CsvDictionary
from .localize import localize


class ResultItem(object):

    def __init__(self, attrs, date_re=None):
        date_re = date_re or '.'
        for attr, value in attrs.items():
            try:
                value = Decimal(value)
            except (InvalidOperation, ValueError):
                try:
                    pattern = re.compile(date_re)
                    if re.match(pattern, str(value)):
                        value = localize(parse(value))
                except (AttributeError, ValueError):
                    pass
            setattr(self, attr, value)

    def as_list(self):
        return [self.__dict__.get(k) for k in self.field_list]


class CsvResults(object):

    def __init__(self, csv_format, filename):
        self.csv_format = csv_format
        self.filename = os.path.expanduser(filename)
        self.field_labels = []
        self.csv_fields = []
        for csv_dictionary in CsvDictionary.objects.filter(csv_format=self.csv_format):
            self.csv_fields.append(csv_dictionary.csv_field)
        for csv_dictionary in CsvDictionary.objects.filter(csv_format=self.csv_format):
            try:
                self.field_labels.append(csv_dictionary.processing_field)
            except AttributeError:
                self.field_labels.append(csv_dictionary.utestid.name)
        self.results = OrderedDict()
        self.load()

    def __iter__(self):
        for result_item in self.results.values():
            yield result_item

    def load(self):
        """Loads the CSV file into a dictionary of ResultItem instances."""
        with open(self.filename, 'r', encoding=self.csv_format.encoding, newline='') as f:
            reader = csv.reader(f, delimiter=self.csv_format.delimiter)
            header_row = next(reader)
            header_row = [h.strip('\t\n\r') for h in header_row]
            if not self.csv_format.get_header_as_list() == header_row:
                raise ValueError('CSV file header row does not match CSV format')
            csv_dictionaries = CsvDictionary.objects.filter(csv_format=self.csv_format)
            for row in reader:
                attrs = OrderedDict()
                field_list = []
                row = dict(zip(header_row, row))
                for csv_dictionary in csv_dictionaries:
                    try:
                        field_label = csv_dictionary.utestid.name
                    except AttributeError:
                        field_label = csv_dictionary.processing_field
                    attrs.update({field_label: row.get(csv_dictionary.csv_field.name)})
                    field_list.append(field_label)
                attrs.update({'field_list': field_list})
                result_item = ResultItem(attrs)
                self.results[result_item.result_identifier] = result_item

    def save(self):
        pass
