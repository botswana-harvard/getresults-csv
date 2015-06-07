from django.contrib import admin

from .models import Result, ResultItem, Panel, PanelItem, PanelMapping, Utestid


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


class PanelItemAdmin(admin.ModelAdmin):
    list_display = ('panel', 'utestid')
    search_fields = ('panel__name', 'utestid__name')
admin.site.register(PanelItem, PanelItemAdmin)


class UtestidAdmin(admin.ModelAdmin):
    pass
admin.site.register(Utestid, UtestidAdmin)
