# file ddisearch/geo/admin.py
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

from django.contrib import admin
from ddisearch.geo.models import Location, GeonamesCountry,  \
    GeonamesContinent, StateCode

class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'geonames_id', 'country_code', 'continent_code',
                    'feature_code', 'latitude', 'longitude', 'state_code')
    list_filter = ('country_code', 'continent_code', 'feature_code', 'state_code')
    search_fields = ('name', 'geonames_id', 'country_code', 'state_code')


class GeonamesCountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'continent', 'geonames_id', 'numeric_code')
    list_filter = ('continent',)
    search_fields = ('name', 'code', 'continent', 'geonames_id', 'numeric_code')


class GeonamesContinentAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'geonames_id')
    search_fields = ('name', 'code', 'geonames_id')

class StateCodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'fips')
    search_fields = ('name', 'code', 'fips')


admin.site.register(Location, LocationAdmin)
admin.site.register(GeonamesCountry, GeonamesCountryAdmin)
admin.site.register(GeonamesContinent, GeonamesContinentAdmin)
admin.site.register(StateCode, StateCodeAdmin)
