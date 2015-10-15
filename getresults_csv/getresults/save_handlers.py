from dmis_models.models import Receive as DmisReceive
from getresults_receive.models import Receive
from getresults_patient.models import Patient
from getresults_aliquot.models import Aliquot
from getresults_order.models import Order, OrderPanel
from getresults_result.models import Result, ResultItem
from getresults_sender.models import SenderPanel
from getresults_aliquot.models.aliquot_type import AliquotType


class Multiset2DMISSaveHandler(object):

    """Save multiset CSV data to DMIS."""

    def get_dmis_receive(self, result_identifier):
        return DmisReceive.objects.get(receive_identifier=result_identifier)

    def save(self, csv_format, csv_results):

        # look up received sample in DMIS
        # create receive, aliquot, order
        # create result, result item
        # result is ready for validation and export to LIS

        for result_identifier, csv_result_item in csv_results.items():
            dmis_receive = self.get_dmis_receive(result_identifier)
            try:
                patient = Patient.objects.get(
                    patient_identifier=dmis_receive.patient_identifier)
            except Patient.DoesNotExist:
                patient = Patient.objects.create(patient_identifier=dmis_receive.patient_identifier)
            try:
                receive = Receive.objects.get(receive_identifier=dmis_receive.receive_identifier)
            except Receive.DoesNotExist:
                receive = Receive.objects.create(
                    receive_identifier=dmis_receive.receive_identifier,
                    patient=patient,
                    collection_datetime=dmis_receive.drawn_datetime,
                    specimen_condition='OK',
                    protocol_number=dmis_receive.protocol_number,
                    specimen_reference=dmis_receive.edc_specimen_identifier)
            try:
                aliquot_type = AliquotType.objects.get(alpha_code='WB')
            except AliquotType.DoesNotExist:
                aliquot_type = AliquotType.objects.create(
                    name='Whole Blood', alpha_code='WB', numeric_code='02')
            try:
                aliquot = Aliquot.objects.get(
                    receive=receive,
                    receive_identifier=receive.receive_identifier,
                    parent_aliquot_identifier__isnull=True)
            except Aliquot.DoesNotExist:
                aliquot = Aliquot.objects.create(
                    receive=receive,
                    receive_identifier=receive.receive_identifier,
                    aliquot_datetime=dmis_receive.receive_datetime,
                    aliquot_type=aliquot_type)
#             sender_panel = SenderPanel.objects.get(name=csv_result_item.panel)
#             order = self.create_order(aliquot, sender_panel)
#             result = Result.objects.create(
#                 order=order)
#             ResultItem.objects.create(result_value=csv_result_item.CD4)
#             ResultItem.objects.create(result_value=csv_result_item.CD8)
#             ResultItem.objects.create(result_value=csv_result_item.CD4_prec)
#             ResultItem.objects.create(result_value=csv_result_item.CD8_perc)
