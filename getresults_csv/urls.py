from django.conf.urls import include, url
from django.contrib import admin


from getresults_csv.views import ImportHistoryView

admin.autodiscover()

urlpatterns = [
    # url(r'^admin/', include(admin_site.urls)),
    url(r'', ImportHistoryView.as_view(), name='importhistory_url'),
]
