from django.conf.urls import patterns, url

from ddisearch.geo import views

urlpatterns = patterns('',
    url(r'^$', views.browse, name='browse'),

)
