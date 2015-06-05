from django.db import models

from .panel import Panel


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

    def __str__(self):
        return '{}: {}'.format(self.specimen_identifier, str(self.panel))

    class _Meta:
        app_label = 'getresults_facs'
        unique_together = ('specimen_identifier', 'collection_datetime')


class ResultItem(models.Model):

    result = models.ForeignKey(Result)

    utestid = models.CharField(
        max_length=10)

    value = models.CharField(
        max_length=25)

    quantifier = models.CharField(
        max_length=3)

    result_datetime = models.DateTimeField()

    def __str__(self):
        return '{}: {}'.format(self.utestid, str(self.result))

    class _Meta:
        app_label = 'getresults_facs'
        unique_together = ('result', 'utestid', 'result_datetime')
