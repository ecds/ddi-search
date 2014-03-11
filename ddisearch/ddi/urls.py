from django.conf.urls import patterns, url

from ddisearch.ddi import views

urlpatterns = patterns('',
    url(r'^search/$', views.search, name='search'),
    url(r'^resources/(?P<agency>[a-zA-Z]+):(?P<id>[0-9]+)/$',
        views.resource, name='resource'),
    url(r'^resources/(?P<agency>[a-zA-Z]+):(?P<id>[0-9]+)/XML/$',
        views.resource_xml, name='xml'),
    url(r'^(?P<mode>(topics|keywords))/$', views.browse_terms,
        name='browse-terms'),
)
