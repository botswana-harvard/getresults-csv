import csv
import os

from collections import OrderedDict
from dateutil import parser


from getresults_facs.models import Panel, PanelMapping, Result, ResultItem

from django.db.utils import IntegrityError


class GetResults:

    def __init__(self, filename, result_cls, encoding=None):
        self.filename = os.path.expanduser(filename)
        self.encoding = encoding or 'utf-8'  # mac_roman
        self.result_cls = result_cls
        self.results = OrderedDict()
        self.load()

    def load(self):
        """Loads the Multiset CSV file into a list of Result instances.

        Expects all results in the CSV file to be of the same panel."""
        panel = None
        with open(self.filename, encoding=self.encoding, newline='') as f:
            reader = csv.reader(f, delimiter='\t')
            header = next(reader)
            for values in reader:
                result = self.result_cls(dict(zip(header, values)))
                self.results[result.specimen_identifier] = result
                if not panel:
                    panel = result.panel
                else:
                    if panel != result.panel:
                        raise ValueError('Expected on panel per file. Got {} then {}.'.format(
                            self.panel, result['Panel Name']))

    def save(self):
        """Saves the CSV data to the local result table."""
        for result in self.results.values():
            try:
                obj = Result.objects.get(
                    specimen_identifier=result.specimen_identifier,
                    panel=result.panel,
                    collection_datetime=result.collection_datetime)
            except Result.DoesNotExist:
                obj = Result.objects.create(
                    specimen_identifier=result.specimen_identifier,
                    panel=result.panel,
                    collection_datetime=result.collection_datetime,
                    analyzer_name=result.analyzer_name,
                    analyzer_sn=result.analyzer_sn,
                    operator=result.operator)
            for item in result.result:
                try:
                    ResultItem.objects.get(
                        result=obj,
                        utestid=item.utestid,
                        result_datetime=item.result_datetime)
                except ResultItem.DoesNotExist:
                    ResultItem.objects.create(
                        result=obj,
                        utestid=item.utestid,
                        value=item.value,
                        quantifier=item.quantifier,
                        result_datetime=item.result_datetime)
