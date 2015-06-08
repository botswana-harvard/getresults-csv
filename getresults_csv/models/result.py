from django.db import models

from simple_history.models import HistoricalRecords

from .panel import Panel
from .import_history import ImportHistory
from .export_history import ExportHistory


class Result(models.Model):

    specimen_identifier = models.CharField(
        max_length=25)

    collection_datetime = models.DateTimeField()

    panel = models.ForeignKey(Panel)

    analyzer_name = models.CharField(
        max_length=25)

    analyzer_sn = models.CharField(
        max_length=25)

    operator = models.CharField(
        max_length=25)

    # validation_history

    import_history = models.ForeignKey(ImportHistory)

    export_history = models.ForeignKey(ExportHistory, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.specimen_identifier, str(self.panel))

    class _Meta:
        app_label = 'getresults_csv'
        unique_together = ('specimen_identifier', 'collection_datetime')
