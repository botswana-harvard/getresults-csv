from django.contrib import admin

from .models import (
    CsvMapping, CsvHeader, CsvHeaderItem, ImportHistory)


class CsvMappingAdmin(admin.ModelAdmin):
    pass
admin.site.register(CsvMapping, CsvMappingAdmin)


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
