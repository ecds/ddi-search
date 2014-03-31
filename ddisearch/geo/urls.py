from django.conf.urls import patterns, url

from ddisearch.geo import views

urlpatterns = patterns('',
    url(r'^$', views.browse, name='browse'),
    url(r'^(?P<continent>[A-Z]{2})/$', views.browse, name='continent'),
    url(r'^(?P<continent>[A-Z]{2})/(?P<country>[A-Z]{2})/$', views.browse,
        name='country'),
    url(r'^(?P<continent>[A-Z]{2})/(?P<country>[A-Z]{2})/(?P<state>[A-Z0-9]{2,3})/$',
        views.browse, name='state'),
    url(r'^(?P<continent>[A-Z]{2})/(?P<country>[A-Z]{2})/(?P<state>[A-Z0-9]{2,3})/(?P<geonames_id>[0-9]+)/$',
        views.browse, name='substate'),
)
