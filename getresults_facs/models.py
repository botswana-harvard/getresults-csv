from django.db import models


class PanelMap(models.Model):

    panel_name = models.CharField(
        max_length=50
    )

    file_field = models.CharField(
        max_length=50
    )

    db_field = models.CharField(
        max_length=10
    )

    class _Meta:
        app_label = 'getresult'
