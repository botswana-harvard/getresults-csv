from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.generic import ListView

from getresults_csv.models import ImportHistory


class ImportHistoryView(ListView):
    queryset = ImportHistory.objects.all().order_by('-import_datetime')
    context_object_name = 'importhistory_list'
    template_name = 'getresults_csv/importhistory_list.html'
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super(ImportHistoryView, self).get_context_data(**kwargs)
        context.update(
            section_title='Import History')
        return context
