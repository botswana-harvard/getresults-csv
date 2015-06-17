import math
import os

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase

from getresults.models import Panel, PanelItem, Utestid, Result, ResultItem, UtestidMapping
from getresults.utils import (
    load_panel_items_from_csv, load_utestids_from_csv, load_panels_from_csv,
    load_utestidmappings_from_csv
)

from ..classes.csv_result_record import CsvResultRecord, CsvResultRecordItem
from ..classes.csv_results import CsvResults
from ..models import ImportHistory, CsvMapping, CsvHeader, CsvHeaderItem
from ..utils import load_csvmapping_from_csv, load_csv_headers_from_csv


class TestGetresult(TestCase):

    def setUp(self):
        """Load testdata."""
        path = os.path.expanduser('~/source/getresults-csv/getresults_csv/testdata/')
        load_panels_from_csv(
            csv_filename=os.path.join(path, 'panels.csv')
        )
        load_csvmapping_from_csv()
        load_utestids_from_csv(
            csv_filename=os.path.join(path, 'utestids.csv')
        )
        load_panel_items_from_csv(
            csv_filename=os.path.join(path, 'panel_items.csv')
        )
        load_csv_headers_from_csv()
        load_utestidmappings_from_csv(
            csv_filename=os.path.join(path, 'utestid_mappings.csv')
        )

    def test_load(self):
        """Assert correct number of records created based on testdata."""
        self.assertEquals(Panel.objects.all().count(), 8)
        self.assertEquals(PanelItem.objects.all().count(), 6)
        self.assertEquals(CsvMapping.objects.all().count(), 29)
        self.assertEquals(Utestid.objects.all().count(), 6)
        self.assertEquals(CsvHeader.objects.all().count(), 2)
        self.assertEquals(CsvHeaderItem.objects.all().count(), 14)
        self.assertEquals(UtestidMapping.objects.all().count(), 5)
#         for obj in UtestidMapping.objects.all():
#             print(obj.sender.name, obj.sender_utestid_name, obj.utestid.name)

    def test_panel_item_string(self):
        """Asserts a string result is imported and formatted correctly."""
        panel = Panel.objects.create(name='Elisa')
        utestid = Utestid.objects.create(
            name='ELISA',
            value_type='absolute',
            value_datatype='string')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid)
        value = panel_item.utestid.value('POS')
        self.assertEquals(value, 'POS')

    def test_panel_item_integer(self):
        """Asserts an integer result is imported and formatted correctly."""
        panel = Panel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer',
        )
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        value = panel_item.utestid.value(100.99)
        self.assertEquals(value, 101)

    def test_panel_item_decimal(self):
        """Asserts a decimal result is imported and formatted correctly."""
        panel = Panel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='decimal',
            precision=1)
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid)
        value = panel_item.utestid.value(100.77)
        self.assertEquals(value, 100.8)

    def test_panel_item_calc(self):
        """Asserts a calculated result is formatted correctly."""
        panel = Panel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMHLOG',
            value_type='calculated',
            value_datatype='decimal',
            precision=2,
            formula='LOG10')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid)
        value = panel_item.utestid.value(750000)
        self.assertEquals(value, round(math.log10(750000), 2))

    def test_header_labels_as_dict(self):
        """Asserts a calculated result is created once the formula_utestid value is available."""
        filename = os.path.join(settings.BASE_DIR, 'testdata/vl.csv')
        header_labels = {
            'panel_name': 'panel_name',
            'analyzer_name': 'analyzer_name',
            'analyzer_sn': 'analyzer_sn',
            'collection_datetime': 'collection_datetime',
            'result_identifier': 'result_identifier',
            'result_datetime': 'result_datetime',
            'operator': 'operator',
        }
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename, header_labels=header_labels, delimiter=',')
        result = csv_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), 2)
        self.assertTrue(ResultItem.objects.filter(result=result, utestid__name='phmlog10').exists())

    def test_header_labels_as_csv_header(self):
        """Asserts a calculated result is created once the formula_utestid value is available."""
        filename = os.path.join(settings.BASE_DIR, 'testdata/vl.csv')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename, csv_header_name='amplicore', delimiter=',')
        result = csv_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), 2)
        self.assertTrue(ResultItem.objects.filter(result=result, utestid__name='phmlog10').exists())

    def test_panel_item_calc_created(self):
        """Asserts a calculated result is created once the formula_utestid value is available."""
        filename = os.path.join(settings.BASE_DIR, 'testdata/vl.csv')
        header_labels = {
            'panel_name': 'panel_name',
            'analyzer_name': 'analyzer_name',
            'analyzer_sn': 'analyzer_sn',
            'collection_datetime': 'collection_datetime',
            'result_identifier': 'result_identifier',
            'result_datetime': 'result_datetime',
            'operator': 'operator',
        }
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename, header_labels=header_labels, delimiter=',')
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

    def test_panel_item_formula(self):
        panel = Panel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMHLOG',
            value_type='calculated',
            value_datatype='decimal',
            precision=2,
            formula='1 + log10(100)')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid,
        )
        self.assertRaises(ValueError, panel_item.utestid.value, 750000)

    def test_panel_item_quantifier_eq(self):
        panel = Panel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid
        )
        value_with_quantifier = panel_item.utestid.value_with_quantifier(1000)
        self.assertEquals(value_with_quantifier, ('=', 1000))

    def test_panel_item_quantifier_lt(self):
        panel = Panel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer',
            lower_limit=400,
            upper_limit=750000)
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid)
        value_with_quantifier = panel_item.utestid.value_with_quantifier(400)
        self.assertEquals(value_with_quantifier, ('=', 400))
        value_with_quantifier = panel_item.utestid.value_with_quantifier(399)
        self.assertEquals(value_with_quantifier, ('<', 400))

    def test_panel_item_quantifier_gt(self):
        panel = Panel.objects.create(name='viral load')
        utestid = Utestid.objects.create(
            name='PMH',
            value_type='absolute',
            value_datatype='integer',
            lower_limit=400,
            upper_limit=750000)
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid=utestid)
        value_with_quantifier = panel_item.utestid.value_with_quantifier(750000)
        self.assertEquals(value_with_quantifier, ('=', 750000))
        value_with_quantifier = panel_item.utestid.value_with_quantifier(750001)
        self.assertEquals(value_with_quantifier, ('>', 750000))

    def test_result(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename)
        for result_record in csv_results:
            self.assertIsInstance(result_record, CsvResultRecord)
            for field in result_record:
                self.assertIsInstance(field, CsvResultRecordItem)
        result_record = csv_results.result_records['AA11540']
        self.assertEquals(result_record.result_identifier, 'AA11540')
        self.assertEquals(result_record.as_dict['cd4'].value, 519)
        self.assertEquals(result_record.as_dict['cd8'].value, 1007)
        self.assertEquals(result_record.as_dict['cd4%'].value, 26)
        self.assertEquals(result_record.as_dict['cd8%'].value, 51)

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

    def test_read_utestidmapping(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        CsvResults.create_dummy_records = True
        csv_results = CsvResults(filename)
        for result_record in csv_results:
            utestids = [u.utestid.name for u in UtestidMapping.objects.filter(sender=result_record.sender)]
            for panel_item in PanelItem.objects.filter(panel=result_record.panel):
                self.assertIn(panel_item.utestid.name, utestids)
