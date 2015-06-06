import pytz

from collections import namedtuple
from dateutil import parser

from django.conf import settings

from ..models import PanelMapping, Panel, Utestid, PanelItem

tz = pytz.timezone(settings.TIME_ZONE)


class PanelResultItem(object):
    """Represents a single result within a panel of results.

    For example CD4 Abs within a CD4 Panel of CD4 Abs, CD4%, CD8 Abs, CD8%.
    """
    def __init__(self, panel_item, utestid, value, result_datetime, source):
        self.panel_item = panel_item
        self.quantifier, self.value = panel_item.quantifier(value)
        self.result_datetime = result_datetime
        self.source = source
        self.utestid = Utestid.objects.get(name=utestid)

    def __repr__(self):
        return '{}({},{}...)'.format(self.__class__.__name__, self.panel_item, self.utestid)

    def __str__(self):
        return '{}: {}{}'.format(self.utestid, self.quantifier, self.value)


class PanelResult(object):
    """Represents a single result within a panel of results.

    For example CD4 Abs within a CD4 Panel of CD4 Abs, CD4%, CD8 Abs, CD8%.
    """
    def __init__(self, result_as_dict, source, labels=None):
        self._as_list = []
        self._as_dict = {}
        self.result_as_dict = result_as_dict
        self.source = source
        self.validated = False
        self.validation_datetime = None
        self.validation_operator = None
        (panel_name, specimen_identifier, collection_datetime,
         result_datetime, analyzer_name, analyzer_sn, operator) = self.parse_labels(labels)
        self.panel = Panel.objects.get(name__iexact=result_as_dict[panel_name].strip())
        self.specimen_identifier = result_as_dict[specimen_identifier]
        self.collection_datetime = tz.localize(parser.parse(result_as_dict[collection_datetime]))
        self.result_datetime = tz.localize(parser.parse(result_as_dict[result_datetime]))
        self.analyzer_name = result_as_dict[analyzer_name]
        self.analyzer_sn = result_as_dict[analyzer_sn]
        self.operator = result_as_dict[operator]

    def __repr__(self):
        return '{}({}: {})'.format(self.__class__.__name__, self.panel, self.source.split('/')[-1])

    def __str__(self):
        return '{}: {}'.format(self.panel, self.source.split('/')[-1])

    def __iter__(self):
        for r in self.as_list:
            yield r

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
    def as_list(self):
        """Returns the result as list of PanelResultItems."""
        if not self._as_list:
            for mapping in PanelMapping.objects.filter(panel=self.panel):
                self._as_list.append(PanelResultItem(
                    panel_item=PanelItem.objects.get(panel=self.panel, utestid=mapping.utestid),
                    utestid=mapping.utestid,
                    value=self.result_as_dict[mapping.csv_field],
                    result_datetime=self.result_datetime,
                    source=self.source,
                ))
        return self._as_list

    @property
    def as_dict(self):
        """Returns the result as dict of PanelResultItems on key utestid."""
        if not self._as_dict:
            for item in self.as_list:
                self._as_dict[item.utestid.name] = item
        return self._as_dict

    def validate(self):
        """Flags a result as validated."""
