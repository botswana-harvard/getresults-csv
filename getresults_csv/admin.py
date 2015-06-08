from django.contrib import admin

from .models import (
    Result, ResultItem, Panel, PanelItem, PanelMapping, Utestid, CsvHeader, CsvHeaderItem, ImportHistory)


class ResultAdmin(admin.ModelAdmin):
    list_display = ('specimen_identifier', 'collection_datetime', 'panel',
                    'operator', 'analyzer_name', 'import_history')
    search_fields = ('specimen_identifier', 'source')
admin.site.register(Result, ResultAdmin)


class ResultItemAdmin(admin.ModelAdmin):
    list_display = ('result', 'utestid', 'value', 'quantifier', 'result_datetime')
    search_fields = ('result__specimen_identifier', 'result__panel__name',
                     'result_datetime', 'result__import_history__source')
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


class CsvHeaderAdmin(admin.ModelAdmin):
    pass
admin.site.register(CsvHeader, CsvHeaderAdmin)


class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ('source', 'import_datetime', 'record_count')
    search_fields = ('source', 'import_datetime', 'record_count')
admin.site.register(ImportHistory, ImportHistoryAdmin)


class CsvHeaderItemAdmin(admin.ModelAdmin):
    list_display = ('csv_header', 'key', 'header_field')
    search_fields = ('csv_header', 'key', 'header_field')
admin.site.register(CsvHeaderItem, CsvHeaderItemAdmin)
