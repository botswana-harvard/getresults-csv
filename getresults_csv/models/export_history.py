from uuid import uuid4

from django.db import models


class ExportHistory(models.Model):

    destination = models.CharField(
        max_length=25)

    export_datetime = models.DateTimeField()

    reference = models.CharField(
        max_length=36,
        default=uuid4)

    class Meta:
        app_label = 'getresults_csv'
        ordering = ('-export_datetime', )
