import csv
import os

from collections import OrderedDict

from getresults.dispatchers import GetResultsDispatcherMixin

from ..models import ImportHistory, CsvHeaderItem, CsvHeader

from .csv_result_record import CsvResultRecord


class CsvResults(GetResultsDispatcherMixin):

    def __init__(self, filename, source=None, encoding=None,
                 delimiter=None, header_labels=None, csv_header_name=None):
        """Loads filename into itself.

        Keywords:
            * source: not tested
            * encoding: if coming from an old MAC, use 'mac_roman' (default: utf-8);
            * delimiter: a valid CSV delimiter;
            * header_labels: a dictionary of {key: header label} where key is a key expected
              by this class and header label is a field in the CSV header;
            * csv_header_name: Does a lookup by this name on CsvHeader and populates
              the header_labels dictionary. If provided and valid overrides header_labels.
        """
        self.filename = os.path.expanduser(filename)
        try:
            self.header_labels = {}
            self.csv_header = CsvHeader.objects.get(name=csv_header_name)
            for item in CsvHeaderItem.objects.filter(csv_header=self.csv_header):
                self.header_labels.update({item.key: item.header_field})
        except CsvHeader.DoesNotExist as e:
            if csv_header_name:
                raise CsvHeader.DoesNotExist('{} Got \'{}\''.format(e, csv_header_name))
            else:
                self.header_labels = header_labels
        self.source = source or str(filename.name)
        self.encoding = encoding or 'utf-8'  # mac_roman
        self.csv_result_records = OrderedDict()
        self.delimiter = delimiter or '\t'
        self.load()

    def __iter__(self):
        for csv_result_record in self.csv_result_records.values():
            yield csv_result_record

    def load(self):
        """Loads the CSV file into a list of Result instances.

        Expects all results in the CSV file to be of the same panel."""
        panel = None
        with open(self.filename, encoding=self.encoding, newline='') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            header = next(reader)
            header = [h.lower() for h in header]
            for values in reader:
                csv_result_record = CsvResultRecord(
                    dict(zip(header, values)),
                    self.filename,
                    header_labels=self.header_labels)
                self.csv_result_records[csv_result_record.result_identifier] = csv_result_record
                if not panel:
                    panel = csv_result_record.panel
                else:
                    if panel != csv_result_record.panel:
                        raise ValueError('Expected one panel per file. Got {} then {}.'.format(
                            self.panel, csv_result_record['Panel Name']))

    def save(self):
        """Saves the CSV data to the local result tables."""
        result_identifiers = []
        for csv_result_record in self.csv_result_records.values():
            patient = self.patient(
                csv_result_record.patient_identifier,
                csv_result_record.gender,
                csv_result_record.dob,
                csv_result_record.registration_datetime)
            order = self.order(
                csv_result_record.order_identifier,
                csv_result_record.order_datetime,
                'X',
                'F',
                csv_result_record.panel,
                patient
            )
            result = self.result(
                order,
                csv_result_record.specimen_identifier,
                csv_result_record.operator,
                csv_result_record.status,
                csv_result_record.instrument)
            result_identifiers.append(str(result.result_identifier))
            for item in csv_result_record.as_list:
                self.result_item(
                    result,
                    item.utestid,
                    item)
        ImportHistory.objects.create(
            result_identifiers=','.join(result_identifiers),
            source=self.source,
            record_count=len(self.csv_result_records.values())
        )
        return result
