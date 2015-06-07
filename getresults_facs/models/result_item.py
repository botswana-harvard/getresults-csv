from django.db import models

from simple_history.models import HistoricalRecords

from ..choices import VALIDATION_CHOICES

from .result import Result
from .utestid import Utestid


class ResultItem(models.Model):

    result = models.ForeignKey(Result)

    utestid = models.ForeignKey(Utestid)

    value = models.CharField(
        max_length=25)

    quantifier = models.CharField(
        max_length=3)

    result_datetime = models.DateTimeField()

    validation = models.CharField(
        max_length=25,
        choices=VALIDATION_CHOICES,
        null=True,
        blank=True)

    validation_operator = models.CharField(
        max_length=25,
        null=True,
        blank=True)

    validation_datetime = models.DateTimeField(
        null=True,
        blank=True)

    history = HistoricalRecords()

    def __str__(self):
        return '{}: {}'.format(self.utestid, str(self.result))

    class Meta:
        app_label = 'getresults_facs'
        unique_together = ('result', 'utestid', 'result_datetime')
