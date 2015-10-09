from datetime import datetime
from dateutil import parser
from uuid import uuid4

from getresults_order.models import OrderPanel, OrderPanelItem
from getresults_sender.models import Sender

from ..models import CsvDefinition

from .csv_result_record_item import CsvResultRecordItem


class CsvResultRecord(object):
    """
    Represents result items for a result line in a csv file.
    """

    def __init__(self, result, source, header_map=None):
        self._as_list = []
        self._as_dict = {}
        self.result = result
        self.source = source
        self.validated = False
        self.validation_datetime = None
        self.validation_operator = None
        try:
            self.order_panel = OrderPanel.objects.get(
                name__iexact=result[header_map.get('order_panel')].strip())
        except OrderPanel.DoesNotExist as e:
            raise OrderPanel.DoesNotExist(
                '{} Got \'{}\''.format(str(e), result[header_map.order_panel].strip()))
        self.result_identifier = result[header_map.result_identifier]
        self.specimen_identifier = result.get(header_map.specimen_identifier)
        self.order_identifier = result.get(header_map.order_identifier)
        self.collection_datetime = self.localize(parser.parse(result[header_map.collection_datetime]))
        self.order_datetime = result.get('order_datetime', datetime.now())
        self.patient_identifier = result.get('patient_identifier', str(uuid4()))
        self.dob = result.get('dob')
        self.gender = result.get('gender')
        self.registration_datetime = self.localize(result.get('registration_datetime', datetime.now()))
        self.result_datetime = self.localize(parser.parse(result[header_map.get('result_datetime')]))
        self.analyzer_name = result[header_map.get('analyzer_name')].strip().lower()
        self.analyzer_sn = result[header_map.get('analyzer_sn')].strip().lower()
        self.instrument = self.analyzer_name
        self.operator = result[header_map.get('operator')]
        self.status = result.get('status', 'F')
        try:
            self.sender = Sender.objects.get(serial_number=self.analyzer_sn)
        except Sender.DoesNotExist as e:
            raise Sender.DoesNotExist(
                '{}. Got serial_number={}.'.format(e, self.analyzer_sn))

    @property
    def aliquot_identifier(self):
        return self.specimen_identifier

    def __repr__(self):
        return '{}({}:{}:{})'.format(
            self.__class__.__name__, self.order_identifier, self.order_panel, self.source.split('/')[-1])

    def __str__(self):
        return '{2}: {0} result from {1}'.format(
            self.order_panel, self.source.split('/')[-1], self.order_identifier)

    def __iter__(self):
        for r in self.as_list:
            yield r

    @property
    def as_list(self):
        """Returns the result as list of PanelResultItems."""
        if not self._as_list:
            for order_panel_item in OrderPanelItem.objects.filter(order_panel=self.order_panel):
                try:
                    csv_definition = CsvDefinition.objects.get(
                        sender_panel_item__sender_panel__sender=self.sender,
                        utestid=order_panel_item.utestid,
                    )
                    key = csv_definition.utest_id.name
                except CsvDefinition.DoesNotExist:
                    if order_panel_item.utestid.formula_utestid_name:
                        key = order_panel_item.utestid.formula_utestid_name
                    else:
                        raise ValueError(
                            'Utestid \'{}\' is not mapped to sender \'{}\'. See '
                            'table CsvDefinition.'.format(order_panel_item.utestid.name, self.sender.name))
                value = self.result[key]
                csv_result_item = CsvResultRecordItem(
                    order_panel_item=order_panel_item,
                    utestid=order_panel_item.utestid,
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
