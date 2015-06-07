from django.db import models

from django.utils import timezone


class ImportHistory(models.Model):

    source = models.CharField(
        max_length=50)

    record_count = models.IntegerField()

    import_datetime = models.DateTimeField(
        default=timezone.now)

    class Meta:
        app_label = 'getresults_facs'
