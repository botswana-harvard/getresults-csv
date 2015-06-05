from django.contrib import admin

from .models import Result, ResultItem, Panel, PanelMapping


class ResultAdmin(admin.ModelAdmin):
    pass
admin.site.register(Result, ResultAdmin)


class ResultItemAdmin(admin.ModelAdmin):
    pass
admin.site.register(ResultItem, ResultItemAdmin)


class PanelAdmin(admin.ModelAdmin):
    pass
admin.site.register(Panel, PanelAdmin)


class PanelMappingAdmin(admin.ModelAdmin):
    pass
admin.site.register(PanelMapping, PanelMappingAdmin)
