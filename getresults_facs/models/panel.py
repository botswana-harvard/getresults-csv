import ast

from math import log10

from django.db import models

from ..choices import VALUE_DATATYPES, VALUE_TYPES


class Panel(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class _Meta:
        app_label = 'getresults_facs'


class PanelItem(models.Model):
    """Model that represents one result item in a panel.

    Has methods to format absolute values and to calculate, then format,
    calculated values. Lower and Upper limits of detection determine the
    quantifier.

    For example:
        * If the lower limit of detection is 400, a value of 400 returns ('=', 400)
          and a value of 399 returns ('<', 400).
        * if the upper limit of detection is 750000, a value of 750000 returns ('=', 750000)
          and a value of 750001 returns ('>', 750000)
    """
    panel = models.ForeignKey(Panel)

    utestid = models.CharField(
        max_length=10,
        help_text=''
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
        help_text='lower limit of detection (exclusive)'
    )

    upper_limit = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        help_text='upper limit of detection (exclusive)'
    )

    precision = models.IntegerField(
        null=True,
    )

    formula = models.CharField(
        max_length=25,
        null=True,
        blank=True,
        help_text='if a calculated value, include an a simple formula or LOG10')

    def value(self, raw_value):
        """Returns the value as the type defined in value_type."""
        if self.value_type == 'calculated':
            raw_value = self.calculated_value(raw_value)
        if self.value_datatype == 'string':
            return str(raw_value)
        elif self.value_datatype == 'integer':
            return int(round(float(raw_value), 0))
        elif self.value_datatype == 'decimal':
            return round(float(raw_value), self.precision)
        else:
            raise ValueError('Attribute value_type may not be None')
        return None

    def calculated_value(self, raw_value):
        """Returns the value as the type defined in value_type.

        Formulas may use basic operators such as 1 + 1 that can be evaluted
        by ast.literla_eval.

        Allowed functions (so far):
            LOG10: if the formula is 'LOG10', the returned value will be log10 of value.
        """
        try:
            value = ast.literal_eval(self.formula.format(value=raw_value))
        except ValueError:
            if self.formula == 'LOG10':
                value = log10(raw_value)
            else:
                raise ValueError('Invalid formula for caluclated value. See {}')
        return value

    def quantifier(self, raw_value):
        """Returns a tuple of (quantifier, value) given a raw value.

        For example:
            * If the lower limit of detection is 400, a value of 400 returns ('=', 400)
              and a value of 399 returns ('<', 400).
            * if the upper limit of detection is 750000, a value of 750000 returns ('=', 750000)
              and a value of 750001 returns ('>', 750000)
        """
        value = self.value(raw_value)
        try:
            if value < self.lower_limit:
                return ('<', self.lower_limit)
            elif value > self.upper_limit:
                return ('>', self.upper_limit)
        except TypeError:
            pass
        return ('=', value)

    class _Meta:
        app_label = 'getresults_facs'
        unique_together = ('panel', 'utestid')


class PanelMapping(models.Model):
    """Model lists map between csv field and the db field by panel name."""

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
