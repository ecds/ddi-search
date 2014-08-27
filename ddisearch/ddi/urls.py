# file ddisearch/ddi/urls.py
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

from django.conf.urls import patterns, url

from ddisearch.ddi import views

urlpatterns = patterns('',
    url(r'^search/$', views.search, name='search'),
    url(r'^resources/(?P<agency>[a-zA-Z0-9]+):(?P<id>[0-9_]+)/$',
        views.resource, name='resource'),
    url(r'^resources/(?P<agency>[a-zA-Z0-9]+):(?P<id>[0-9_]+)/XML/$',
        views.resource_xml, name='xml'),
    url(r'^(?P<mode>(topics|keywords))/$', views.browse_terms,
        name='browse-terms'),
)
