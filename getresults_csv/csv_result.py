import csv
import os
import re

from collections import OrderedDict
from dateutil.parser import parse
from decimal import Decimal, InvalidOperation

from .choices import PROCESS_FIELDS
from .localize import localize
from .models import CsvDictionary


class BaseSaveHandler(object):

    def save(self, csv_format, results):
        for order_identifier, csv_result_item in results.items():
            print(order_identifier, csv_result_item.as_list())


class CsvResultItem(object):
    """A simple class that represents one result from the CSV file by commonly
    named attributes.

    The CsvDictionary for this csv_format maps a CSV field to the correct
    instance attribute. CsvDictionary "processing fields" map to required instance
    attributes that are common to all csv_result_items while utestid fields
    are specific to the sender panel. See CsvDictionary."""

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
            try:
                setattr(self, attr, value.strip())
            except AttributeError:
                setattr(self, attr, value)
        missing_attrs = self.missing_attrs()
        if missing_attrs:
            raise TypeError(
                'Some required attrs are not defined. Check csv dictionary '
                'for this files csv format. Missing {}.'.format(missing_attrs))

    def missing_attrs(self):
        """Returns None if all required attrs exist in the instance dictionary."""
        return [k for k in self.required_attrs if k not in self.as_dict()]

    @property
    def required_attrs(self):
        return [x[0] for x in PROCESS_FIELDS]

    def as_list(self):
        return [self.__dict__.get(k) for k in self.field_list]

    def as_dict(self):
        return {k: v for k, v in self.__dict__.items() if k in self.field_list}


class CsvResult(object):

    def __init__(self, csv_format, filename, save_handler=None):
        self.csv_format = csv_format
        self.filename = os.path.expanduser(filename)
        if save_handler:
            self.save_handler = save_handler
        else:
            self.save_handler = BaseSaveHandler()
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

    def __repr__(self):
        return '{0}({1}, {2})'.format(
            self.__class__.__name__, self.csv_format.name, self.filename)

    def __str__(self):
        return (self.csv_format, self.filename)

    def __iter__(self):
        for csv_result_item in self.results.values():
            yield csv_result_item

    def load(self):
        """Loads the CSV file into a dictionary of CsvResultItem instances."""
        with open(self.filename, 'r', encoding=self.csv_format.encoding, newline='') as f:
            reader = csv.reader(f, delimiter=self.csv_format.delimiter)
            header_row = next(reader)
            header_row = [h.strip('\t\n\r') for h in header_row]
            if not self.csv_format.get_header_as_list() == header_row:
                raise ValueError('CSV file header row does not match csv format {}'.format(self.csv_format.name))
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
                csv_result_item = CsvResultItem(attrs)
                self.results[csv_result_item.order_identifier] = csv_result_item

    def save(self):
        self.save_handler.save(self.csv_format, self.results)
