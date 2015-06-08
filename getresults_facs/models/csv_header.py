from django.db import models

KEYS = (
    ('analyzer_name', 'analyzer_name'),
    ('analyzer_sn', 'analyzer_sn'),
    ('collection_datetime', 'collection_datetime'),
    ('operator', 'operator'),
    ('panel_name', 'panel_name'),
    ('utestid_name', 'utestid_name'),
    ('result_datetime', 'result_datetime'),
    ('specimen_identifier', 'specimen_identifier'),
)


class CsvHeader(models.Model):

    name = models.CharField(
        max_length=25,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_facs'


class CsvHeaderItem(models.Model):

    csv_header = models.ForeignKey(CsvHeader)

    key = models.CharField(
        max_length=25,
        choices=KEYS)

    header_field = models.CharField(
        max_length=25)

    def __str__(self):
        return '{}: {}'.format(str(self.csv_header), self.key)

    class Meta:
        app_label = 'getresults_facs'
        unique_together = (('csv_header', 'key'), ('csv_header', 'header_field'))