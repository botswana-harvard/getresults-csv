import math
import os

from django.test import TestCase
from django.conf import settings

from ..classes.panel_result import PanelResultItem, PanelResult
from ..getresults import GetResults
from ..models import Panel, Result, ResultItem, Panel, PanelItem
from ..utils import load_panels_from_csv, load_utestids_from_csv, load_panel_items_from_csv


class TestGetresult(TestCase):

    def setUp(self):
        load_panels_from_csv()
        load_utestids_from_csv()
        load_panel_items_from_csv()

    def test_load(self):
        for panel in Panel.objects.all():
            print(panel.name)

    def test_panel_item_string(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='absolute',
            value_datatype='string')
        value = panel_item.value('POS')
        self.assertEquals(value, 'POS')

    def test_panel_item_integer(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='absolute',
            value_datatype='integer')
        value = panel_item.value(100.99)
        self.assertEquals(value, 101)

    def test_panel_item_decimal(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='absolute',
            value_datatype='decimal',
            precision=1)
        value = panel_item.value(100.77)
        self.assertEquals(value, 100.8)

    def test_panel_item_calc(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='calculated',
            value_datatype='decimal',
            precision=2,
            formula='LOG10'
        )
        value = panel_item.value(750000)
        self.assertEquals(value, round(math.log10(750000), 2))

    def test_panel_item_formula(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='calculated',
            value_datatype='decimal',
            precision=2,
            formula='1 + log10(100)'
        )
        self.assertRaises(ValueError, panel_item.value, 750000)

    def test_panel_item_quantifier_eq(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='absolute',
            value_datatype='integer',
        )
        quantifier = panel_item.quantifier(1000)
        self.assertEquals(quantifier, ('=', 1000))

    def test_panel_item_quantifier_lt(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='absolute',
            value_datatype='integer',
            lower_limit=400,
            upper_limit=750000
        )
        quantifier = panel_item.quantifier(400)
        self.assertEquals(quantifier, ('=', 400))
        quantifier = panel_item.quantifier(399)
        self.assertEquals(quantifier, ('<', 400))

    def test_panel_item_quantifier_gt(self):
        panel = Panel.objects.create(name='viral load')
        panel_item = PanelItem.objects.create(
            panel=panel,
            utestid='PSM',
            value_type='absolute',
            value_datatype='integer',
            lower_limit=400,
            upper_limit=750000
        )
        quantifier = panel_item.quantifier(750000)
        self.assertEquals(quantifier, ('=', 750000))
        quantifier = panel_item.quantifier(750001)
        self.assertEquals(quantifier, ('>', 750000))

    def test_result(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        get_results = GetResults(filename)
        for panel_result in get_results:
            self.assertIsInstance(panel_result, PanelResult)
            for panel_result_item in panel_result:
                self.assertIsInstance(panel_result_item, PanelResultItem)
        panel_result = get_results.panel_results['AA11540']
        self.assertEquals(panel_result.specimen_identifier, 'AA11540')
        self.assertEquals(panel_result.as_dict['CD4'].value, 519)
        self.assertEquals(panel_result.as_dict['CD8'].value, 1007)
        self.assertEquals(panel_result.as_dict['CD4%'].value, 26)
        self.assertEquals(panel_result.as_dict['CD8%'].value, 51)

    def test_result_save(self):
        filename = os.path.join(settings.BASE_DIR, 'testdata/rad9A6A3.tmp')
        get_results = GetResults(filename)
        get_results.save()
