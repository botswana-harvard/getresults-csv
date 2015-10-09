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

from .classes import CsvResultRecord, CsvResultRecordItem, CsvResults
from .models import ImportHistory, CsvDefinition, Header, HeaderItem
from .utils import load_csv_definitions_from_csv, load_csv_headers_from_csv


class DummyAliquot(BaseAliquot):

    class Meta:
        app_label = 'getresults_csv'


class TestGetresults(TestCase):

    def setUp(self):
        """Load testdata."""
        load_utestids_from_csv()
        load_sender_panels_from_csv()
        load_order_panels_from_csv()
        load_senders_from_csv()
        load_csv_headers_from_csv()
        load_csv_definitions_from_csv()

    def test_load(self):
        """Assert correct number of records created based on testdata."""
        self.assertEquals(OrderPanel.objects.all().count(), 8)
        self.assertEquals(OrderPanelItem.objects.all().count(), 6)
        self.assertEquals(Utestid.objects.all().count(), 6)
        self.assertEquals(Header.objects.all().count(), 2)
        self.assertEquals(HeaderItem.objects.all().count(), 14)
        self.assertEquals(SenderPanel.objects.all().count(), 30)
        self.assertEquals(CsvDefinition.objects.all().count(), 29)

    def test_ordered_header_row_as_dict(self):
        """Asserts a calculated result is created once the formula_utestid value is available."""
        filename = os.path.join(settings.BASE_DIR, 'testdata/vl.csv')
        ordered_header_row = {
            'panel_name': 'panel_name',
            'analyzer_name': 'analyzer_name',
            'analyzer_sn': 'analyzer_sn',
            'collection_datetime': 'collection_datetime',
            'result_identifier': 'result_identifier',
            'result_datetime': 'result_datetime',
            'operator': 'operator',
        }
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename, ordered_header_row=ordered_header_row, delimiter=',')
        result = csv_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), 2)
        self.assertTrue(ResultItem.objects.filter(result=result, utestid__name='phmlog10').exists())

    def test_ordered_header_row_as_csv_header(self):
        """Asserts a calculated result is created once the formula_utestid value is available."""
        filename = os.path.join(settings.BASE_DIR, 'testdata/vl.csv')
        csv_results = CsvResults(filename, header_name='amplicore', delimiter=',')
        print(csv_results.csv_result_records)
        result = csv_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), 2)
        self.assertTrue(ResultItem.objects.filter(result=result, utestid__name='phmlog10').exists())

    def test_panel_item_calc_created(self):
        """Asserts a calculated result is created once the formula_utestid value is available."""
        filename = os.path.join(settings.BASE_DIR, 'testdata/vl.csv')
        ordered_header_row = {
            'panel_name': 'panel_name',
            'analyzer_name': 'analyzer_name',
            'analyzer_sn': 'analyzer_sn',
            'collection_datetime': 'collection_datetime',
            'result_identifier': 'result_identifier',
            'result_datetime': 'result_datetime',
            'operator': 'operator',
        }
        csv_results = CsvResults(filename, ordered_header_row=ordered_header_row, delimiter=',')
        result = csv_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), 2)
        self.assertTrue(ResultItem.objects.filter(result=result, utestid__name='phmlog10').exists())
        expected = [('AA99991', 1100), ('AA99992', 400), ('AA99993', 750000), ('AA99994', 399), ('AA99995', 800000)]
        for specimen_identifier, raw_value in expected:
            result_item = ResultItem.objects.get(
                result__specimen_identifier=specimen_identifier,
                utestid__name='phm',
            )
            self.assertEquals(result_item.raw_value, str(raw_value), (specimen_identifier, raw_value))
            self.assertEquals(
                result_item.raw_value,
                str(raw_value),
                (specimen_identifier, raw_value))
        for specimen_identifier, raw_value in expected:
            result_item = ResultItem.objects.get(
                result__specimen_identifier=specimen_identifier,
                utestid__name='phmlog10',
            )
            self.assertEquals(
                result_item.value,
                str(result_item.utestid.value(raw_value)),
                (specimen_identifier, raw_value))
            self.assertEquals(
                result_item.raw_value,
                str(raw_value),
                (specimen_identifier, raw_value))

    def test_result(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename, header_name='multiset')
        for csv_result_record in csv_results:
            self.assertIsInstance(csv_result_record, CsvResultRecord)
            for csv_result_record_item in csv_result_record:
                self.assertIsInstance(csv_result_record_item, CsvResultRecordItem)
        csv_result_record = csv_results.csv_result_records['AA11540']
        self.assertEquals(csv_result_record.result_identifier, 'AA11540')
        self.assertEquals(csv_result_record.as_dict['cd4'].reportable_value, ('=', 519))
        self.assertEquals(csv_result_record.as_dict['cd8'].reportable_value, ('=', 1007))
        self.assertEquals(csv_result_record.as_dict['cd4%'].reportable_value, ('=', 26))
        self.assertEquals(csv_result_record.as_dict['cd8%'].reportable_value, ('=', 51))

    def test_result_save(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename)
        csv_results.save()

    def test_import_history(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename)
        csv_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)

    def test_result_duplicate(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename)
        csv_results.save()
        source = str(filename.name)
        import_history = ImportHistory.objects.get(source=source)
        result_identifiers = import_history.result_identifiers
        self.assertTrue(ResultItem.objects.filter(
            result__result_identifier__in=result_identifiers.split(',')).exists())
        result_count = Result.objects.filter(result_identifier=import_history.result_identifiers.split(',')).count()
        result_item_count = ResultItem.objects.filter(
            result__result_identifier__in=result_identifiers.split(',')).count()
        self.assertGreater(result_item_count, 0)
        csv_results = CsvResults(filename)
        csv_results.save()
        self.assertRaises(MultipleObjectsReturned, ImportHistory.objects.get, source=source)
        self.assertEquals(Result.objects.filter(
            result_identifier__in=import_history.result_identifiers).count(), result_count)
        self.assertEquals(ResultItem.objects.filter(
            result__result_identifier__in=import_history.result_identifiers.split(',')).count(), result_item_count)

    def test_read_sender(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename)
        for result_record in csv_results:
            self.assertEquals(result_record.sender.name, 'e12334567890')
