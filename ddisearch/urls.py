# file ddisearch/urls.py
#
# Copyright 2014 Emory University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.sitemaps import views as sitemaps_views
from django.views.generic import TemplateView

from ddisearch.ddi.sitemaps import sitemap_cfg

admin.autodiscover()


urlpatterns = [
    # Examples:
    # url(r'^$', 'ddisearch.views.home', name='home'),
     url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
        content_type='text/plain')),
    url(r'^$', 'ddisearch.ddi.views.site_index', name='site-index'),
    url(r'^', include('ddisearch.ddi.urls', namespace='ddi')),
    url(r'^places/', include('ddisearch.geo.urls', namespace='geo')),

    url(r'^admin/', include(admin.site.urls)),

    # xml sitemaps for search-engine discovery
    url(r'^sitemap\.xml$', sitemaps_views.index, {'sitemaps': sitemap_cfg},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemaps_views.sitemap,
        {'sitemaps': sitemap_cfg}),
]