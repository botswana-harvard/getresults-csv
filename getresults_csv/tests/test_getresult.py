import math
import os

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.test import TestCase

from ..classes.panel_result import PanelResultItem, PanelResult
from ..getresults import GetResults
from ..models import Panel, PanelItem, Utestid, ImportHistory, Result, ResultItem, PanelMapping
from ..utils import load_panels_from_csv, load_utestids_from_csv, load_panel_items_from_csv


class TestGetresult(TestCase):

    def setUp(self):
        """Load testdata."""
        load_panels_from_csv()
        load_utestids_from_csv()
        load_panel_items_from_csv()

    def test_load(self):
        """Assert correct number of records created based on testdata."""
        self.assertEquals(Panel.objects.all().count(), 8)
        self.assertEquals(PanelItem.objects.all().count(), 6)
        self.assertEquals(PanelMapping.objects.all().count(), 29)
        self.assertEquals(Utestid.objects.all().count(), 6)

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
        value = panel_item.value('POS')
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
        value = panel_item.value(100.99)
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
        value = panel_item.value(100.77)
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
        value = panel_item.value(750000)
        self.assertEquals(value, round(math.log10(750000), 2))

    def test_panel_item_calc_created(self):
        """Asserts a calculated result is created once the formula_utestid value is available."""
        filename = os.path.join(settings.BASE_DIR, 'testdata/vl.csv')
        labels = {
            'panel_name': 'panel_name',
            'analyzer_name': 'analyzer_name',
            'analyzer_sn': 'analyzer_sn',
            'collection_datetime': 'collection_datetime',
            'specimen_identifier': 'specimen_identifier',
            'phm': 'phm',
            'result_datetime': 'result_datetime',
            'operator': 'operator',
        }
        get_results = GetResults(filename, labels=labels, delimiter=',')
        result = get_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), 2)
        self.assertTrue(ResultItem.objects.filter(result=result, utestid__name='phmlog10').exists())

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
        self.assertRaises(ValueError, panel_item.value, 750000)

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
        value_with_quantifier = panel_item.value_with_quantifier(1000)
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
        value_with_quantifier = panel_item.value_with_quantifier(400)
        self.assertEquals(value_with_quantifier, ('=', 400))
        value_with_quantifier = panel_item.value_with_quantifier(399)
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
        value_with_quantifier = panel_item.value_with_quantifier(750000)
        self.assertEquals(value_with_quantifier, ('=', 750000))
        value_with_quantifier = panel_item.value_with_quantifier(750001)
        self.assertEquals(value_with_quantifier, ('>', 750000))

    def test_result(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        get_results = GetResults(filename)
        for panel_result in get_results:
            self.assertIsInstance(panel_result, PanelResult)
            for panel_result_item in panel_result:
                self.assertIsInstance(panel_result_item, PanelResultItem)
        panel_result = get_results.panel_results['AA11540']
        self.assertEquals(panel_result.specimen_identifier, 'AA11540')
        self.assertEquals(panel_result.as_dict['cd4'].value, 519)
        self.assertEquals(panel_result.as_dict['cd8'].value, 1007)
        self.assertEquals(panel_result.as_dict['cd4%'].value, 26)
        self.assertEquals(panel_result.as_dict['cd8%'].value, 51)

    def test_result_save(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        get_results = GetResults(filename)
        get_results.save()

    def test_import_history(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        get_results = GetResults(filename)
        get_results.save()
        source = str(filename.name)
        self.assertEquals(ImportHistory.objects.get(source=source).source, source)

    def test_result_duplicate(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        get_results = GetResults(filename)
        get_results.save()
        source = str(filename.name)
        import_history = ImportHistory.objects.get(source=source)
        result = Result.objects.filter(import_history=import_history)
        self.assertTrue(ResultItem.objects.filter(result=result).exists())
        result_count = Result.objects.filter(import_history=import_history).count()
        result_item_count = ResultItem.objects.filter(result=result).count()
        self.assertGreater(result_item_count, 0)
        get_results = GetResults(filename)
        get_results.save()
        self.assertRaises(MultipleObjectsReturned, ImportHistory.objects.get, source=source)
        self.assertEquals(Result.objects.filter(import_history=import_history).count(), result_count)
        self.assertEquals(ResultItem.objects.filter(result=result).count(), result_item_count)
