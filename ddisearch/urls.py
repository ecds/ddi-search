from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.sitemaps import views as sitemaps_views
from django.views.generic import TemplateView

from ddisearch.ddi.sitemaps import sitemap_cfg

admin.autodiscover()


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ddisearch.views.home', name='home'),
     url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
        content_type='text/plain')),
    url(r'^$', 'ddisearch.ddi.views.site_index', name='site-index'),
    url(r'^', include('ddisearch.ddi.urls', namespace='ddi')),
    url(r'^places/', include('ddisearch.geo.urls', namespace='geo')),

    url(r'^admin/', include(admin.site.urls)),

    # xml sitemaps for search-engine discovery
    (r'^sitemap\.xml$', sitemaps_views.index, {'sitemaps': sitemap_cfg}),
    (r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap,
         {'sitemaps': sitemap_cfg}),
)