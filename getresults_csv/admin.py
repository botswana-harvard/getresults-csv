from django.contrib import admin

from edc_base.modeladmin.admin import LimitedAdminInlineMixin
from getresults.admin import admin_site

from .models import ExportHistory, ImportHistory, CsvFormat, CsvField, CsvDictionary
from getresults_csv.forms import CsvDictionaryForm


class CsvFieldAdmin(admin.ModelAdmin):
    list_display = ('csv_format', 'name')
admin_site.register(CsvField, CsvFieldAdmin)


class CsvDictionaryAdmin(admin.ModelAdmin):
    form = CsvDictionaryForm
    list_display = ('csv_format', 'csv_field', 'processing_field', 'utestid')
    search_fields = ('csv_field', 'processing_field', 'utestid__name')
admin_site.register(CsvDictionary, CsvDictionaryAdmin)


class CsvDictionaryInline(LimitedAdminInlineMixin, admin.TabularInline):
    model = CsvDictionary
    form = CsvDictionaryForm
    extra = 0

    def get_filters(self, obj):
        if obj:
            return (('csv_field', dict(csv_format=obj.id)),)
        else:
            return ()


class CsvFormatAdmin(admin.ModelAdmin):
    inlines = [CsvDictionaryInline]
admin_site.register(CsvFormat, CsvFormatAdmin)


class ImportHistoryAdmin(admin.ModelAdmin):
    list_display = ('source', 'import_datetime', 'record_count')
    search_fields = ('source', 'import_datetime', 'record_count')
admin_site.register(ImportHistory, ImportHistoryAdmin)


class ExportHistoryAdmin(admin.ModelAdmin):
    list_display = ('destination', 'export_datetime', 'reference')
    search_fields = ('destination', 'export_datetime', 'reference')
admin_site.register(ExportHistory, ExportHistoryAdmin)
