import csv
import os
from dateutil.parser import parser
from django.utils import timezone
from collections import OrderedDict
from getresults_patient.models import Patient
from getresults_receive.models import Receive
from getresults_aliquot.models.aliquot import Aliquot

from ..models import ImportHistory, HeaderItem
from ..utils import localize

from .csv_result_record import CsvResultRecord


class HeaderMap:

    def __init__(self, **kwargs):
        self.order_panel = kwargs.get('order_panel')
        self.result_identifier = kwargs.get('result_identifier')
        self.specimen_identifier = kwargs.get('specimen_identifier')
        self.order_identifier = kwargs.get('order_identifier')
        self.collection_datetime = self.localize(parser.parse(kwargs.get('collection_datetime')))
        self.patient_identifier = kwargs.get('patient_identifier')
        self.order_panel = kwargs.get('order_panel')
        self.order_panel = kwargs.get('order_panel')


class CsvResults(object):

    def __init__(self, filename, header_name=None, header_map=None, encoding=None,
                 delimiter=None):
        """Loads filename into itself.

        Keywords:
            * encoding: if coming from an old MAC, use 'mac_roman' (default: utf-8);
            * delimiter: a valid CSV delimiter;
            * header_map: a dictionary of {key: header field} where key is a key expected
              by this class and header field is a field from the header row in the csv file;
            * header_name: If header_map not provided does a lookup by this name
              on CsvHeader to get the header_map.
        """
        self.filename = os.path.expanduser(filename)
        if header_map:
            self.header_map = header_map or HeaderMap
        else:
            self.header_map = HeaderItem.objects.header(header_name)
        self.encoding = encoding or 'utf-8'  # mac_roman
        self.csv_result_records = OrderedDict()
        self.delimiter = delimiter or '\t'
        self.load()

    def __iter__(self):
        for csv_result_record in self.csv_result_records.values():
            yield csv_result_record

    def load(self):
        """Loads the CSV file into a list of Result instances.

        Expects all results in the CSV file to be of the same order_panel."""
        order_panel = None
        with open(self.filename, encoding=self.encoding, newline='') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            header = next(reader)
            header = [h.strip('\t\n\r') for h in header]
            unknown_fields = [h for h in self.header_map.values() if h not in header]
            if unknown_fields:
                raise ValueError(
                    'Header row from the csv file does not match the header_map. Got {}'.format(
                        unknown_fields))
            for values in reader:
                csv_result_record = CsvResultRecord(
                    dict(zip(header, values)),
                    self.filename,
                    header_map=self.header_map)
                self.csv_result_records[csv_result_record.result_identifier] = csv_result_record
                if not order_panel:
                    order_panel = csv_result_record.order_panel
                else:
                    if order_panel != csv_result_record.order_panel:
                        raise ValueError('Expected one order_panel per file. Got {} then {}.'.format(
                            self.order_panel, csv_result_record.order_panel))

    def save(self):
        pass
