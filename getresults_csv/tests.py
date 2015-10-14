import os
from os.path import join
from django.conf import settings
from django.test import TestCase

from getresults_order.models import Utestid
from getresults_sender.models import Sender, SenderModel
from getresults_csv.csv_result import CsvResult, BaseSaveHandler
from getresults_csv.models import CsvFormat, CsvField, CsvDictionary
from getresults_csv.configure import Configure
from getresults_csv.csv_file_handler import CsvFileHandler


class TestGetresults(TestCase):

    def setUp(self):
        sender_model = SenderModel.objects.create(name='FACSCalibur', make='BD')
        self.sender = Sender.objects.create(serial_number='E43523', sender_model=sender_model)
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
        return join(
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
        csv_result = CsvResult(self.csv_format, self.sample_filename())
        for csv_result_item in csv_result:
            self.assertEqual([x for x in csv_result_item.as_list() if x is None], [])

    def test_configure_and_import_from_files(self):
        Configure(join(settings.BASE_DIR, 'testdata'))

    def test_file_handler(self):

        class DoNothingSaveHandler(BaseSaveHandler):

            def save(self, csv_format, results):
                pass

        source_dir = join(os.path.dirname(os.path.realpath(__file__)), 'testdata')
        file_patterns = ['*.csv']
        event_handler = CsvFileHandler(
            csv_format=self.csv_format,
            source_dir=source_dir,
            archive_dir=None,
            patterns=file_patterns,
            save_handler=DoNothingSaveHandler(),
            verbose=False)
        event_handler.process_existing_files()
