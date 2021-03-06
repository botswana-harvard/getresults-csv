import codecs
import os
import csv

from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from edc_base.model.models import BaseUuidModel
from getresults_csv.choices import PROCESS_FIELDS
from getresults_order.models import Utestid
from getresults_sender.models import SenderModel

try:
    path = settings.CSV_FILE_PATH
except AttributeError:
    path = '~/'

try:
    file_ext = settings.CSV_FILE_EXT[1]
except (AttributeError, IndexError):
    file_ext = "sample*.*.csv"

DELIMITERS = (
    (',', 'Comma'),
    ('\t', 'Tab'),
    (';', 'Semi-colon'),
    ('|', 'Pipe')
)

ENCODINGS = (
    ('utf_8', 'utf-8'),
    ('mac_roman', 'mac-roman'),
    ('latin_1', 'latin-1'),
    ('utf_16', 'utf-16'),
)


class CsvFormat(BaseUuidModel):

    name = models.CharField(max_length=25, unique=True)

    sender_model = models.ForeignKey(SenderModel, null=True, blank=True)

    header_string = models.TextField(null=True, blank=True)

    sample_file = models.FilePathField(
        match=file_ext,
        path=os.path.expanduser(path),
        help_text=('a file to read the header_string from. '
                   'See also settings.CSV_FILE_PATH and CSV_FILE_EXT'),
        null=True,
        blank=True,
    )

    delimiter = models.CharField(
        max_length=5,
        choices=DELIMITERS,
        default=',')

    encoding = models.CharField(
        max_length=25,
        choices=ENCODINGS,
        default='utf-8'
    )

    def save(self, *args, **kwargs):
        if self.sample_file:
            self.read_sample_header()
        super(CsvFormat, self).save(*args, **kwargs)

    def __str__(self):
        return self.name

    def read_sample_header(self):
        delimiter = codecs.decode(self.delimiter, 'unicode_escape')
        with open(self.sample_file, 'r', encoding=self.encoding) as f:
            reader = csv.reader(f, delimiter=delimiter)
            header = next(reader)
        self.header_field_count = len(header)
        self.header_string = '|'.join(header)
        self.sample_file = None

    def get_header_as_list(self):
        if not self.header_string:
            return []
        return [h for h in self.header_string.split('|')]

    class Meta:
        app_label = 'getresults_csv'


class CsvField(BaseUuidModel):

    csv_format = models.ForeignKey(CsvFormat)

    name = models.CharField(
        max_length=25,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_csv'
        ordering = ('csv_format__name', 'name')
        unique_together = (('csv_format', 'name'), )


class CsvDictionary(BaseUuidModel):

    csv_format = models.ForeignKey(CsvFormat)

    field_label = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        editable=False)

    processing_field = models.CharField(
        max_length=25,
        choices=PROCESS_FIELDS,
        null=True,
        blank=True)

    utestid = models.ForeignKey(Utestid, null=True, blank=True)

    csv_field = models.ForeignKey(CsvField)

    def save(self, *args, **kwargs):
        if self.field_label:
            try:
                self.utestid = Utestid.objects.get(name=self.field_label)
            except Utestid.DoesNotExist:
                self.processing_field = self.field_label
            self.field_label = None
        super(CsvDictionary, self).save(*args, **kwargs)

    def __str__(self):
        return '{}: {}'.format(str(self.csv_format), self.processing_field or str(self.utestid))

    class Meta:
        app_label = 'getresults_csv'
        ordering = ('csv_format__name', 'processing_field')


class ExportHistory(BaseUuidModel):

    destination = models.CharField(
        max_length=25)

    export_datetime = models.DateTimeField()

    reference = models.CharField(
        max_length=36,
        default=uuid4)

    class Meta:
        app_label = 'getresults_csv'
        ordering = ('-export_datetime', )


class ImportHistory(BaseUuidModel):

    success = models.BooleanField(default=False)

    source = models.CharField(
        max_length=50)

    record_count = models.IntegerField(null=True)

    import_datetime = models.DateTimeField(
        default=timezone.now)

    result_identifiers = models.TextField(null=True)

    archive = models.CharField(
        max_length=100, null=True)

    description = models.TextField(null=True)

    message = models.TextField(null=True)

    def __str__(self):
        return '{}: {}'.format(self.source, self.import_datetime)

    class Meta:
        app_label = 'getresults_csv'
        ordering = ('-import_datetime', )


class FileImport(BaseUuidModel):

    source_filename = models.CharField(
        max_length=50)

    archive_filename = models.CharField(
        max_length=50)

    record_count = models.IntegerField(null=True)

    imported = models.BooleanField(default=False)

    import_datetime = models.DateTimeField(
        default=timezone.now)

    description = models.TextField(null=True)

    def __str__(self):
        return '{}: {}'.format(self.source_filename, self.import_datetime)

    class Meta:
        app_label = 'getresults_csv'
        ordering = ('-import_datetime', )


@receiver(post_save, weak=False, dispatch_uid='post_create_csv_format_fields')
def post_create_csv_format_fields(sender, instance, raw, created, using, update_fields, **kwargs):
    if not raw:
        try:
            header_list = instance.get_header_as_list()
            for fld in header_list:
                try:
                    CsvField.objects.get(
                        csv_format=instance,
                        name=fld
                    )
                except CsvField.DoesNotExist:
                    CsvField.objects.create(
                        csv_format=instance,
                        name=fld)
        except AttributeError:
            pass
