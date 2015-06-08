from django.db import models

from getresults_csv import Panel


class PanelMapping(models.Model):
    """Model lists map between csv field and the utestid in the panel."""

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
        return '{}: {}'.format(self.utestid, str(self.panel))

    class Meta:
        app_label = 'getresults_csv'
        unique_together = (
            ('panel', 'csv_field_name'),
            ('panel', 'utestid_name')
        )
        ordering = ('panel', 'utestid_name')
