from django.db import models

from getresults_csv import VALUE_DATATYPES, VALUE_TYPES


class Utestid(models.Model):

    name = models.CharField(
        max_length=10,
        unique=True
    )

    description = models.CharField(
        max_length=50,
    )

    value_type = models.CharField(
        max_length=25,
        choices=VALUE_TYPES,
    )
    value_datatype = models.CharField(
        max_length=25,
        choices=VALUE_DATATYPES,
    )

    lower_limit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='lower limit of detection (exclusive)'
    )

    upper_limit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        help_text='upper limit of detection (exclusive)'
    )

    precision = models.IntegerField(
        null=True,
        blank=True,
    )

    formula = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        help_text='if a calculated value, include an a simple formula or LOG10')

    formula_utestid_name = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text='formula is based on the value of this utestid'
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_csv'
