from django.db import models


class Panel(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class _Meta:
        app_label = 'getresults_facs'


class PanelMapping(models.Model):
    """Model lists map between field field and the db field by panel name."""

    panel = models.ForeignKey(Panel)

    csv_field = models.CharField(
        max_length=50,
        help_text='field name in Multiset file'
    )

    utestid = models.CharField(
        max_length=10,
        help_text='field name in local db table'
    )

    def __str__(self):
        return '{}: {}'.format(self.utestid, str(self.panel))

    class _Meta:
        app_label = 'getresults_facs'
