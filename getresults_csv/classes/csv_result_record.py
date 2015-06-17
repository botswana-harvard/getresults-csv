import pytz

from datetime import datetime
from dateutil import parser
from uuid import uuid4

from django.conf import settings

from getresults.models import Panel, Sender, PanelItem, UtestidMapping

from .csv_result_record_item import CsvResultRecordItem

tz = pytz.timezone(settings.TIME_ZONE)


class CsvResultRecord(object):
    """
    Represents result items for a result line in a csv file.
    """
    def __init__(self, result_as_dict, source, header_labels=None):
        self._as_list = []
        self._as_dict = {}
        self.result_as_dict = result_as_dict
        self.source = source
        self.validated = False
        self.validation_datetime = None
        self.validation_operator = None
        lbl_panel_name = self.parse_header_labels(header_labels, 'panel_name', 'panel name')
        lbl_specimen_identifier = self.parse_header_labels(header_labels, 'specimen_identifier', 'sample id')
        lbl_order_identifier = self.parse_header_labels(header_labels, 'order_identifier', 'sample id')
        lbl_result_identifier = self.parse_header_labels(header_labels, 'result_identifier', 'sample id')
        lbl_collection_datetime = self.parse_header_labels(header_labels, 'collection_datetime', 'collection date')
        lbl_result_datetime = self.parse_header_labels(header_labels, 'result_datetime', 'date analyzed')
        lbl_analyzer_name = self.parse_header_labels(header_labels, 'analyzer_name', 'cytometer')
        lbl_analyzer_sn = self.parse_header_labels(header_labels, 'analyzer_sn', 'cytometer serial number')
        lbl_operator = self.parse_header_labels(header_labels, 'operator', 'operator')
        try:
            self.panel = Panel.objects.get(name__iexact=result_as_dict[lbl_panel_name].strip())
        except Panel.DoesNotExist as e:
            raise Panel.DoesNotExist('{} Got \'{}\''.format(str(e), result_as_dict[lbl_panel_name].strip()))
        self.result_identifier = result_as_dict[lbl_result_identifier]
        self.specimen_identifier = result_as_dict.get(lbl_specimen_identifier, self.result_identifier)
        self.order_identifier = result_as_dict.get(lbl_order_identifier, self.result_identifier)
        self.collection_datetime = tz.localize(parser.parse(result_as_dict[lbl_collection_datetime]))
        self.order_datetime = result_as_dict.get('order_datetime', datetime.now())
        self.patient_identifier = result_as_dict.get('patient_identifier', str(uuid4()))
        self.dob = result_as_dict.get('dob', None)
        self.gender = result_as_dict.get('gender', None)
        self.registration_datetime = result_as_dict.get('registration_datetime', datetime.now())
        self.result_datetime = tz.localize(parser.parse(result_as_dict[lbl_result_datetime]))
        self.analyzer_name = result_as_dict[lbl_analyzer_name].strip().lower()
        self.analyzer_sn = result_as_dict[lbl_analyzer_sn].strip().lower()
        self.instrument = self.analyzer_name
        self.operator = result_as_dict[lbl_operator]
        self.status = result_as_dict.get('status', 'F')
        try:
            self.sender = Sender.objects.get(name=self.analyzer_sn)
        except Sender.DoesNotExist as e:
            raise Sender.DoesNotExist(
                '{}. Update Sender and UtestidMapping. Got {}.'.format(e, self.analyzer_sn))

    def __repr__(self):
        return '{}({}:{}:{})'.format(
            self.__class__.__name__, self.order_identifier, self.panel, self.source.split('/')[-1])

    def __str__(self):
        return '{2}: {0} result from {1}'.format(
            self.panel, self.source.split('/')[-1], self.order_identifier)

    def __iter__(self):
        for r in self.as_list:
            yield r

    def parse_header_labels(self, header_labels, key, default):
        try:
            return header_labels[key]
        except (KeyError, TypeError):
            return default

    @property
    def as_list(self):
        """Returns the result as list of PanelResultItems."""
        if not self._as_list:
            for panel_item in PanelItem.objects.filter(panel=self.panel):
                try:
                    utestid_mapping = UtestidMapping.objects.get(
                        sender=self.sender,
                        utestid=panel_item.utestid
                    )
                    key = utestid_mapping.sender_utestid_name
                except UtestidMapping.DoesNotExist:
                    if panel_item.utestid.formula_utestid_name:
                        key = panel_item.utestid.formula_utestid_name
                    else:
                        raise ValueError(
                            'Utestid \'{}\' is not mapped to sender \'{}\'. See '
                            'table UtestidMapping.'.format(panel_item.utestid.name, self.sender.name))
                value = self.result_as_dict[key]
                csv_result_item = CsvResultRecordItem(
                    panel_item=panel_item,
                    utestid=panel_item.utestid,
                    value=value,
                    result_datetime=self.result_datetime,
                    status=self.status,
                    sender=self.sender,
                    operator=self.operator,
                )
                self._as_list.append(csv_result_item)
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
