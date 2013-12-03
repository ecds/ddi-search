from django.conf.urls import patterns, url

from ddisearch.ddi import views

urlpatterns = patterns('',
    url(r'^search/$', views.search, name='search'),
)
