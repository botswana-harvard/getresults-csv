from django.contrib import admin

from .models import (
    Header, HeaderItem, ExportHistory, ImportHistory, CsvDefinition)


class CsvDefinitionAdmin(admin.ModelAdmin):
    pass
admin.site.register(CsvDefinition, CsvDefinitionAdmin)


class HeaderAdmin(admin.ModelAdmin):
    pass
admin.site.register(Header, HeaderAdmin)


class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ('source', 'import_datetime', 'record_count')
    search_fields = ('source', 'import_datetime', 'record_count')
admin.site.register(ImportHistory, ImportHistoryAdmin)


class HeaderItemAdmin(admin.ModelAdmin):
    list_display = ('csv_header', 'key', 'header_field')
    search_fields = ('csv_header', 'key', 'header_field')
admin.site.register(HeaderItem, HeaderItemAdmin)


class ExportHistoryAdmin(admin.ModelAdmin):
    list_display = ('source', 'export_datetime', 'record_count')
    search_fields = ('source', 'export_datetime', 'record_count')
admin.site.register(ExportHistory, ExportHistoryAdmin)
