from django.db import models

from edc_base.model.models import BaseUuidModel

from getresults.models import Panel


class CsvMapping(BaseUuidModel):
    """Model lists map between csv field and the utestid in the panel.

    Note: the CSV file does not necessarily fill in all values for a panel
        since some panel_items are calculated."""

    panel = models.ForeignKey(Panel)

    csv_field_name = models.CharField(
        max_length=50,
        help_text='field name in Multiset file'
    )

    utestid_name = models.CharField(
        max_length=10,
        help_text=''
    )

    def __str__(self):
        return '{}: {}'.format(self.utestid_name, str(self.panel))

    class Meta:
        app_label = 'getresults_csv'
        unique_together = (
            ('panel', 'csv_field_name'),
            ('panel', 'utestid_name')
        )
        ordering = ('panel', 'utestid_name')
