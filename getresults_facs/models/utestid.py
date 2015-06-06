from django.db import models


class Utestid(models.Model):

    name = models.CharField(
        max_length=10,
        unique=True
    )

    quantifier = models.CharField(
        max_length=3,
        default='=',
    )

    description = models.CharField(
        max_length=50,
    )

    def __str__(self):
        return self.name

    class _Meta:
        app_label = 'getresults_facs'
