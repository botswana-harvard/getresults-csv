import csv
import os

from collections import OrderedDict

from getresults.models import Result, ResultItem, Panel, Order

from ..models import ImportHistory, CsvHeaderItem, CsvHeader

from .panel_result import PanelResult


class CsvResults(object):

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
        self.panel_results = OrderedDict()
        self.delimiter = delimiter or '\t'
        self.load()

    def __iter__(self):
        for panel_result in self.panel_results.values():
            yield panel_result

    def load(self):
        """Loads the CSV file into a list of Result instances.

        Expects all results in the CSV file to be of the same panel."""
        panel = None
        with open(self.filename, encoding=self.encoding, newline='') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            header = next(reader)
            header = [h.lower() for h in header]
            for values in reader:
                panel_result = PanelResult(dict(zip(header, values)), self.filename,
                                           header_labels=self.header_labels)
                self.panel_results[panel_result.result_identifier] = panel_result
                if not panel:
                    panel = panel_result.panel
                else:
                    if panel != panel_result.panel:
                        raise ValueError('Expected one panel per file. Got {} then {}.'.format(
                            self.panel, panel_result['Panel Name']))

    def result(self, panel_result, order):
        try:
            result = Result.objects.get(
                result_identifier=panel_result.result_identifier,
                order__panel=panel_result.panel,
                collection_datetime=panel_result.collection_datetime)
        except Result.DoesNotExist:
            result = Result.objects.create(
                result_identifier=panel_result.result_identifier,
                order=order,
                specimen_identifier=panel_result.specimen_identifier,
                collection_datetime=panel_result.collection_datetime,
                analyzer_name=panel_result.analyzer_name,
                analyzer_sn=panel_result.analyzer_sn,
                operator=panel_result.operator,
                # validation_datetime=None,
                # validation_operator=None,
                # validation=None,
                # import_history=import_history,
                # export_history=None,
            )
        return result

    def result_item(self, result, panel_result_item):
        try:
            result_item = ResultItem.objects.get(
                result=result,
                utestid=panel_result_item.utestid,
                result_datetime=panel_result_item.result_datetime)
        except ResultItem.DoesNotExist:
            result_item = ResultItem.objects.create(
                result=result,
                utestid=panel_result_item.utestid,
                value=panel_result_item.value,
                quantifier=panel_result_item.quantifier,
                result_datetime=panel_result_item.result_datetime,
                # validation_datetime=None,
                # validation_operator=None,
                # validation=None,
            )
        return result_item

    def panel(self, name):
        try:
            panel = Panel.objects.get(name=name)
        except Panel.DoesNotExist:
            panel = Panel.objects.create(name=name)
        return panel

    def order(self, panel_result):
        try:
            order = Order.objects.get(order_identifier=panel_result.order_identifier)
        except Order.DoesNotExist:
            order = Order.objects.create(
                order_identifier=panel_result.order_identifier,
                specimen_identifier=panel_result.specimen_identifier,
                panel=panel_result.panel)
        return order

    def save(self):
        """Saves the CSV data to the local result tables."""
        result_identifiers = []
        for panel_result in self.panel_results.values():
            order = self.order(panel_result)
            result = self.result(panel_result, order)
            result_identifiers.append(result.result_identifier)
            for panel_result_item in panel_result.as_list:
                self.result_item(result, panel_result_item)
        ImportHistory.objects.create(
            result_identifiers=','.join(result_identifiers),
            source=self.source,
            record_count=len(self.panel_results.values())
        )
        # self.archive_file(self.filename)
        return result
