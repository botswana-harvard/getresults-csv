from django.conf.urls import include, url
from django.contrib import admin


from getresults.admin import admin_site
from getresults import urls as getresults_urls

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin_site.urls)),
    url(r'', include(getresults_urls)),
]
