import re
from copy import copy
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from dmis_models.models import Receive as DmisReceive
from getresults_aliquot.models import Aliquot
from getresults_aliquot.models.aliquot_type import AliquotType
from getresults_order.models import Order, OrderPanelItem
from getresults_receive.models import Receive
from getresults_result.models import Result, ResultItem
from getresults_sender.models import SenderPanel


class Multiset2DMISSaveHandler(object):

    """Save multiset CSV data to DMIS."""

    identifier_exclude_patterns = [r'^[0-9]{6}$', r'^[0-9]{5}$']
    file_patterns = [file_ext[0] for file_ext in settings.CSV_FILE_EXT]

    def __init__(self):
        identifier_exclude_patterns = copy(self.identifier_exclude_patterns)
        for identifier_exclude_pattern in identifier_exclude_patterns:
            self.identifier_exclude_patterns.append(re.compile(identifier_exclude_pattern))

    def get_dmis_receive(self, order_identifier):
        """Dmis has no "order" prior to result. Sample is tested on the receive
        identifier. so start assume receive identifier and order_identifer are the same."""
        for identifier_exclude_pattern in self.identifier_exclude_patterns:
            if re.match(identifier_exclude_pattern, str(order_identifier)):
                print('skipping {}'.format(order_identifier))
                return None
        try:
            receive = DmisReceive.objects.get(receive_identifier=order_identifier)
        except DmisReceive.DoesNotExist:
            print('skipping {}. Not received.'.format(order_identifier))
            receive = None
        return receive

    def get_order(self, order_identifier, collection_date, sender_panel):
        try:
            order = Order.objects.get(order_identifier=order_identifier)
        except Order.DoesNotExist:
            try:
                receive = Receive.objects.get(receive_identifier=order_identifier)
            except Receive.DoesNotExist:
                receive = Receive.objects.create(
                    receive_identifier=order_identifier,
                    collection_datetime=collection_date)
            try:
                aliquot_type = AliquotType.objects.get(alpha_code='WB')
            except AliquotType.DoesNotExist:
                aliquot_type = AliquotType.objects.create(alpha_code='WB', numeric_code='02')
            try:
                aliquot = Aliquot.objects.get(receive_identifier=order_identifier)
            except Aliquot.DoesNotExist:
                aliquot = Aliquot.objects.create(
                    receive=receive,
                    aliquot_type=aliquot_type)
            order = Order.objects.create(
                order_identifier=order_identifier,
                order_datetime=collection_date,
                order_panel=sender_panel.order_panel,
                aliquot=aliquot,
            )
        return order

    def save(self, csv_format, csv_results):

        # look up received sample in DMIS
        # create receive, aliquot, order
        # create result, result item
        # result is ready for validation and export to LIS

        for order_identifier, csv_result_item in csv_results.items():
            dmis_receive = self.get_dmis_receive(order_identifier)
            if dmis_receive:
                try:
                    sender_panel = SenderPanel.objects.get(name=csv_result_item.sender_panel)
                except SenderPanel.DoesNotExist as e:
                    raise ObjectDoesNotExist('{} Got \'{}\''.format(e, csv_result_item.sender_panel))
                order = self.get_order(
                    order_identifier=dmis_receive.receive_identifier,
                    collection_date=csv_result_item.collection_date,
                    sender_panel=sender_panel)
                result = Result.objects.create(
                    order=order,
                    specimen_identifier=csv_result_item.order_identifier,
                    collection_datetime=csv_result_item.collection_date,
                    analyzer_name=csv_result_item.sender,
                    analyzer_sn=csv_result_item.serial_number,
                    operator=csv_result_item.operator)
                for order_panel_item in OrderPanelItem.objects.filter(order_panel=sender_panel.order_panel):
                    try:
                        result = ResultItem.objects.get(
                            result=result,
                            utestid=order_panel_item.utestid)
                        result.value = getattr(csv_result_item, order_panel_item.utestid.name)
                        result.raw_value = getattr(csv_result_item, order_panel_item.utestid.name)
                        result.quantifier = '='
                        result.result_datetime = csv_result_item.result_datetime
                        result.sender = csv_result_item.sender
                        result.save()
                    except ResultItem.DoesNotExist:
                        ResultItem.objects.create(
                            result=result,
                            utestid=order_panel_item.utestid,
                            value=getattr(csv_result_item, order_panel_item.utestid.name),
                            raw_value=getattr(csv_result_item, order_panel_item.utestid.name),
                            quantifier='=',
                            result_datetime=csv_result_item.result_datetime,
                            sender=csv_result_item.sender,
                            source='')

    def save_to_dmis(self):
        pass
