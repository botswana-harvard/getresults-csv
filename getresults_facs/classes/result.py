import pytz

from collections import namedtuple
from dateutil import parser

from django.conf import settings

from ..models import PanelMapping, Panel

tz = pytz.timezone(settings.TIME_ZONE)


class Result:

    ResultItemTuple = namedtuple('ResultItemTuple', 'utestid value quantifier result_datetime')

    def __init__(self, result_as_dict, labels=None):
        self._result = []
        self.as_dict = result_as_dict
        (panel_name, specimen_identifier, collection_datetime,
         result_datetime, analyzer_name, analyzer_sn, operator) = self.parse_labels(labels)
        self.panel = Panel.objects.get(name__iexact=result_as_dict[panel_name].strip())
        self.mapping = PanelMapping.objects.filter(panel=self.panel)
        self.specimen_identifier = self.as_dict[specimen_identifier]
        self.collection_datetime = tz.localize(parser.parse(self.as_dict[collection_datetime]))
        self.result_datetime = tz.localize(parser.parse(self.as_dict[result_datetime]))
        self.analyzer_name = self.as_dict[analyzer_name]
        self.analyzer_sn = self.as_dict[analyzer_sn]
        self.operator = self.as_dict[operator]

    def parse_labels(self, labels):
        try:
            panel_name = labels['panel_name']
        except (KeyError, TypeError):
            panel_name = 'Panel Name'
        try:
            specimen_identifier = labels['specimen_identfier']
        except (KeyError, TypeError):
            specimen_identifier = 'Sample ID'
        try:
            collection_datetime = labels['collection_datetime']
        except (KeyError, TypeError):
            collection_datetime = 'Collection Date'
        try:
            result_datetime = labels['result_datetime']
        except (KeyError, TypeError):
            result_datetime = 'Date Analyzed'
        try:
            analyzer_name = labels['analyzer_name']
        except (KeyError, TypeError):
            analyzer_name = 'Cytometer'
        try:
            analyzer_sn = labels['analyzer_sn']
        except (KeyError, TypeError):
            analyzer_sn = 'Cytometer Serial Number'
        try:
            operator = labels['operator']
        except (KeyError, TypeError):
            operator = 'Operator'
        return (panel_name, specimen_identifier, collection_datetime,
                result_datetime, analyzer_name, analyzer_sn, operator)

    @property
    def result(self):
        """Returns the result as a namedtuple (utestid, value, quantifier, result_datetime)."""
        if not self._result:
            for mapping in self.mapping:
                self._result.append(self.ResultItemTuple(
                    utestid=mapping.utestid,
                    value=self.as_dict[mapping.csv_field],
                    quantifier='=',
                    result_datetime=self.result_datetime))
        return self._result
