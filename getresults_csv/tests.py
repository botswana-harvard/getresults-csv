import csv
import os

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase

from getresults_aliquot.models import BaseAliquot
from getresults_order.models import OrderPanel, OrderPanelItem, Utestid
from getresults_order.utils import load_utestids_from_csv, load_order_panels_from_csv
from getresults_result.models import Result, ResultItem
from getresults_sender.models import SenderPanel
from getresults_sender.utils import load_sender_panels_from_csv, load_senders_from_csv

from .csv_results import CsvResults
from getresults_csv.models import CsvFormat, CsvField, CsvDictionary, ImportHistory
from getresults_csv.configure import Configure


class DummyAliquot(BaseAliquot):

    class Meta:
        app_label = 'getresults_csv'


class TestGetresults(TestCase):

    def setUp(self):
        self.csv_format = CsvFormat.objects.create(
            name='Multiset',
            sample_file=self.sample_filename(),
            delimiter='\t')
        self.assertEqual(self.csv_format.header_field_count, 278)
        self.csv_format_vl = CsvFormat.objects.create(
            name='VL',
            sample_file=self.sample_filename(filename='vl.csv'),
            delimiter=',')
        self.assertEqual(self.csv_format_vl.header_field_count, 8)
        self.create_csv_dictionary_for_cd4()
        self.create_csv_dictionary_for_vl()

    def sample_filename(self, filename=None):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)), 'testdata/{}'.format(filename or 'rad9A6A3.csv'))

    def create_csv_dictionary(self, csv_format, processing_fields, attrs):
        for processing_field, csv_field in processing_fields.items():
            csv_field_instance = CsvField.objects.get(csv_format=csv_format, name=csv_field)
            CsvDictionary.objects.create(
                csv_format=csv_format,
                processing_field=processing_field,
                csv_field=csv_field_instance
            )
        for utestid, csv_field in attrs.items():
            csv_field_instance = CsvField.objects.get(csv_format=csv_format, name=csv_field)
            utestid_instance = Utestid.objects.get(pk=utestid)
            CsvDictionary.objects.create(
                csv_format=csv_format,
                utestid=utestid_instance,
                csv_field=csv_field_instance
            )

    def create_csv_dictionary_for_vl(self):
        processing_fields = dict(
            collection_date='collection_datetime',
            operator='operator',
            result_datetime='result_datetime',
            result_identifier='result_identifier',
            sender='analyzer_name',
            sender_panel='panel_name',
            serial_number='analyzer_sn'
        )
        PHM = Utestid.objects.create(
            name='PHM', value_type='absolute', value_datatype='integer', units='copies/ml')
        attrs = {str(PHM.pk): 'phm'}
        self.create_csv_dictionary(self.csv_format_vl, processing_fields, attrs)

    def create_csv_dictionary_for_cd4(self):
        processing_fields = dict(
            collection_date='Collection Date',
            operator='Operator',
            result_datetime='Date Analyzed',
            result_identifier='Sample ID',
            sender='Cytometer',
            sender_panel='Panel Name',
            serial_number='Cytometer Serial Number'
        )
        CD4 = Utestid.objects.create(
            name='CD4', value_type='absolute', value_datatype='integer', units='cells/mL')
        CD8_perc = Utestid.objects.create(
            name='CD8%', value_type='absolute', value_datatype='integer', units='cells/mL')
        CD8 = Utestid.objects.create(
            name='CD8', value_type='absolute', value_datatype='integer', units='cells/mL')
        CD4_perc = Utestid.objects.create(
            name='CD4%', value_type='absolute', value_datatype='integer', units='cells/mL')
        attrs = {
            str(CD4.pk): '(Average) CD3+CD4+ Abs Cnt',
            str(CD8_perc.pk): '(Average) CD3+CD8+ %Lymph',
            str(CD8.pk): '(Average) CD3+CD8+ Abs Cnt',
            str(CD4_perc.pk): '(Average) CD3+CD4+ %Lymph'}
        self.create_csv_dictionary(self.csv_format, processing_fields, attrs)

    def test_csv_format_reads_header_row(self):
        csv_format = CsvFormat.objects.create(
            sample_file=self.sample_filename(),
            delimiter='\t')
        self.assertEqual(csv_format.header_field_count, 278)
        self.assertEqual(CsvField.objects.filter(csv_format=csv_format).count(), 278)

    def test_can_read_file_with_dictionary(self):
        field_labels = []
        for csv_dictionary in CsvDictionary.objects.filter(csv_format=self.csv_format):
            try:
                field_labels.append(csv_dictionary.processing_field)
            except AttributeError:
                field_labels.append(csv_dictionary.utestid.name)
        csv_results = CsvResults(self.csv_format, self.sample_filename())
        for result_item in csv_results:
            self.assertEqual([x for x in result_item.as_list() if x is None], [])

    def test_configure_and_import_from_files(self):
        configure = Configure(os.path.join(settings.BASE_DIR, 'testdata'))

#     def test_result(self):
#         file_format = CsvFormat.objects.get(name='multiset')
#         csv_results = CsvResults(self.sample_filename, file_format='multiset')
#         for csv_result_record in csv_results:
#             self.assertIsInstance(csv_result_record, CsvResultRecord)
#             for csv_result_record_item in csv_result_record:
#                 self.assertIsInstance(csv_result_record_item, CsvResultRecordItem)
#         csv_result_record = csv_results.csv_result_records['AA11540']
#         self.assertEquals(csv_result_record.result_identifier, 'AA11540')
#         self.assertEquals(csv_result_record.as_dict['cd4'].reportable_value, ('=', 519))
#         self.assertEquals(csv_result_record.as_dict['cd8'].reportable_value, ('=', 1007))
#         self.assertEquals(csv_result_record.as_dict['cd4%'].reportable_value, ('=', 26))
#         self.assertEquals(csv_result_record.as_dict['cd8%'].reportable_value, ('=', 51))

#     def test_result_save(self):
#         filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
#         CsvResults.create_dummy_records = True
#         csv_results = CsvResults(filename)
#         csv_results.save()

#     def test_result_duplicate(self):
#         filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
#         CsvResults.create_dummy_records = True
#         csv_results = CsvResults(filename)
#         csv_results.save()
#         source = str(filename.name)
#         import_history = ImportHistory.objects.get(source=source)
#         result_identifiers = import_history.result_identifiers
#         self.assertTrue(ResultItem.objects.filter(
#             result__result_identifier__in=result_identifiers.split(',')).exists())
#         result_count = Result.objects.filter(result_identifier=import_history.result_identifiers.split(',')).count()
#         result_item_count = ResultItem.objects.filter(
#             result__result_identifier__in=result_identifiers.split(',')).count()
#         self.assertGreater(result_item_count, 0)
#         csv_results = CsvResults(filename)
#         csv_results.save()
#         self.assertRaises(MultipleObjectsReturned, ImportHistory.objects.get, source=source)
#         self.assertEquals(Result.objects.filter(
#             result_identifier__in=import_history.result_identifiers).count(), result_count)
#         self.assertEquals(ResultItem.objects.filter(
#             result__result_identifier__in=import_history.result_identifiers.split(',')).count(), result_item_count)
# 
#     def test_read_sender(self):
#         filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
#         CsvResults.create_dummy_records = True
#         csv_results = CsvResults(filename)
#         for result_record in csv_results:
#             self.assertEquals(result_record.sender.name, 'e12334567890')
