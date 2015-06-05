from django.test import TestCase
from django.conf import settings

from ..models import Panel, Result, ResultItem
from ..utils import load_panels_from_csv


class TestGetresult(TestCase):

    def setUp(self):
        load_panels_from_csv()

    def test_load(self):
        for panel in Panel.objects.all():
            print(panel.name)
