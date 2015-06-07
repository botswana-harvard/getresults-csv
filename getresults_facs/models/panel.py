from django.db import models


class Panel(models.Model):

    name = models.CharField(
        max_length=50,
        unique=True
    )

    def __str__(self):
        return self.name

    class Meta:
        app_label = 'getresults_facs'
        ordering = ('name', )
