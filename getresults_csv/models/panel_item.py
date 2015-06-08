import ast

from math import log10

from django.db import models

from .panel import Panel
from .utestid import Utestid


class PanelItem(models.Model):
    """Model that represents one item in a panel.

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

    utestid = models.ForeignKey(Utestid)

    def __str__(self):
        return '{}: {}'.format(self.utestid.name, self.panel.name)

    def value(self, raw_value, value_type=None):
        """Returns the value as the type defined in value_type."""
        value_type = value_type or self.utestid.value_type
        if self.utestid.value_type == 'calculated':
            raw_value = self.calculated_value(raw_value)
        if self.utestid.value_datatype == 'string':
            return str(raw_value)
        elif self.utestid.value_datatype == 'integer':
            return int(round(float(raw_value), 0))
        elif self.utestid.value_datatype == 'decimal':
            return round(float(raw_value), self.utestid.precision)
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
            value = ast.literal_eval(self.utestid.formula.format(value=raw_value))
        except ValueError:
            if self.utestid.formula == 'LOG10':
                value = log10(float(raw_value))
            else:
                raise ValueError('Invalid formula for caluclated value. See {}')
        return value

    def value_with_quantifier(self, raw_value):
        """Returns a tuple of (quantifier, value) given a raw value.

        For example:
            * If the lower limit of detection is 400, a value of 400 returns ('=', 400)
              and a value of 399 returns ('<', 400).
            * if the upper limit of detection is 750000, a value of 750000 returns ('=', 750000)
              and a value of 750001 returns ('>', 750000)
        """
        value = self.value(raw_value)
        try:
            if value < self.utestid.lower_limit:
                return ('<', self.value(self.utestid.lower_limit, 'absolute'))
            elif value > self.utestid.upper_limit:
                return ('>', self.value(self.utestid.upper_limit, 'absolute'))
        except TypeError:
            pass
        return ('=', value)

    class Meta:
        app_label = 'getresults_csv'
        unique_together = ('panel', 'utestid')
        ordering = ('panel', 'utestid')
