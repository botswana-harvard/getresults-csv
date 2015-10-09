from uuid import uuid4

from django.db import models
from django.utils import timezone

from edc_base.model.models import BaseUuidModel
from getresults_order.models import Utestid
from getresults_sender.models import SenderPanel


KEYS = (
    ('analyzer_name', 'analyzer_name'),
    ('analyzer_sn', 'analyzer_sn'),
    ('collection_datetime', 'collection_datetime'),
    ('operator', 'operator'),
    ('panel_name', 'panel_name'),
    ('utestid_name', 'utestid_name'),
    ('result_datetime', 'result_datetime'),
    ('result_identifier', 'result_identifier'),
)


class Header(BaseUuidModel):

    name = models.CharField(
        max_length=25,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_csv'


class HeaderManager(models.Manager):

    def header(self, name):
        header_map = {}
        try:
            header = Header.objects.get(name=name)
            for item in self.filter(header=header):
                header_map.update({item.key: item.header_field})
        except Header.DoesNotExist:
            pass
        return header_map


class HeaderItem(BaseUuidModel):

    header = models.ForeignKey(Header)

    key = models.CharField(
        max_length=25,
        choices=KEYS)

    header_field = models.CharField(
        max_length=25)

    objects = HeaderManager()

    def __str__(self):
        return '{}: {}'.format(str(self.header), self.key)

    class Meta:
        app_label = 'getresults_csv'
        unique_together = (('header', 'key'), ('header', 'header_field'))


class CsvDefinition(BaseUuidModel):
    """Model lists map between csv field and the utestid in the panel.

    Note: the CSV file does not necessarily fill in all values for a panel
        since some panel_items are calculated."""

    sender_panel = models.ForeignKey(SenderPanel)

    utestid = models.ForeignKey(Utestid)

    field_name = models.CharField(
        max_length=50,
        help_text='field name in csv file'
    )

    delimiter = models.CharField(
        max_length=5,
        default=',')

    def __str__(self):
        return '{}: {}'.format(self.utestid, str(self.field_name))

    class Meta:
        app_label = 'getresults_csv'
        unique_together = (
            ('sender_panel', 'field_name', 'utestid'),
        )
        ordering = ('sender_panel', 'utestid')


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

    result_identifiers = models.TextField(null=True)

    source = models.CharField(
        max_length=50)

    record_count = models.IntegerField()

    import_datetime = models.DateTimeField(
        default=timezone.now)

    def __str__(self):
        return '{}: {}'.format(self.source, self.import_datetime)

    class Meta:
        app_label = 'getresults_csv'
        ordering = ('-import_datetime', )
