from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ddisearch.views.home', name='home'),
    url(r'^$', 'ddisearch.ddi.views.site_index', name='site-index'),
   # url(r'^blog/', include('blog.urls')),
    url(r'^', include('ddisearch.ddi.urls', namespace='ddi')),

    url(r'^admin/', include(admin.site.urls)),
)
