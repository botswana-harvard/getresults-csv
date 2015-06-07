import csv
import os

from collections import OrderedDict

from .classes import PanelResult
from .models import Result, ResultItem, ImportHistory


class GetResults(object):

    def __init__(self, filename, source=None, encoding=None, delimiter=None, labels=None):
        self.filename = os.path.expanduser(filename)
        self.source = source or str(filename.name)
        self.encoding = encoding or 'utf-8'  # mac_roman
        self.panel_results = OrderedDict()
        self.labels = labels
        self.delimiter = delimiter or '\t'
        self.load()

    def __iter__(self):
        for panel_result in self.panel_results.values():
            yield panel_result

    def load(self):
        """Loads the Multiset CSV file into a list of Result instances.

        Expects all results in the CSV file to be of the same panel."""
        panel = None
        with open(self.filename, encoding=self.encoding, newline='') as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            header = next(reader)
            header = [h.lower() for h in header]
            for values in reader:
                panel_result = PanelResult(dict(zip(header, values)), self.filename, labels=self.labels)
                self.panel_results[panel_result.specimen_identifier] = panel_result
                if not panel:
                    panel = panel_result.panel
                else:
                    if panel != panel_result.panel:
                        raise ValueError('Expected one panel per file. Got {} then {}.'.format(
                            self.panel, panel_result['Panel Name']))

    def save(self):
        """Saves the CSV data to the local result table."""
        import_history = ImportHistory.objects.create(
            source=self.source,
            record_count=len(self.panel_results.values())
        )
        for panel_result in self.panel_results.values():
            try:
                result = Result.objects.get(
                    specimen_identifier=panel_result.specimen_identifier,
                    panel=panel_result.panel,
                    collection_datetime=panel_result.collection_datetime)
            except Result.DoesNotExist:
                result = Result.objects.create(
                    specimen_identifier=panel_result.specimen_identifier,
                    panel=panel_result.panel,
                    collection_datetime=panel_result.collection_datetime,
                    analyzer_name=panel_result.analyzer_name,
                    analyzer_sn=panel_result.analyzer_sn,
                    operator=panel_result.operator,
                    # validation_datetime=None,
                    # validation_operator=None,
                    # validation=None,
                    import_history=import_history,
                    export_history=None,
                )
            for item in panel_result.as_list:
                try:
                    ResultItem.objects.get(
                        result=result,
                        utestid=item.utestid,
                        result_datetime=item.result_datetime)
                except ResultItem.DoesNotExist:
                    ResultItem.objects.create(
                        result=result,
                        utestid=item.utestid,
                        value=item.value,
                        quantifier=item.quantifier,
                        result_datetime=item.result_datetime,
                        validation_datetime=None,
                        validation_operator=None,
                        validation=None,
                    )
        return result
