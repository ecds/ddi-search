# file ddisearch/geo/templatetags/geo_tags.py
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

from django import template
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.utils.safestring import mark_safe

from ddisearch.geo.models import Location, GeonamesContinent, \
    GeonamesCountry

register = template.Library()

@register.filter
def location_url(dbloc):
    '''Generate a browse url for a :class:`~ddisearch.ddi.models.location`'''
    if isinstance(dbloc, Location):
        # continent
        if dbloc.feature_code == 'CONT':
            return reverse('geo:continent',
             kwargs={'continent': dbloc.continent_code})

        # for anything lower than a cntinent, we can't generate geo browse URL
        # without both country and continent codes
        if not dbloc.country_code or not dbloc.continent_code:
                return ''

        # country-level
        country_codes = ['TERR', 'PPLC']
        if dbloc.feature_code.startswith('PCL') or dbloc.feature_code in country_codes:
            return reverse('geo:country',
                kwargs={'continent': dbloc.continent_code, 'country': dbloc.country_code})

        # for state or substate, can't generate url without state code
        if not dbloc.state_code:
            return ''

        # state
        if dbloc.feature_code in ['ADM1', 'RGN']:
            return reverse('geo:state',
                kwargs={'continent': dbloc.continent_code, 'country': dbloc.country_code,
                        'state': dbloc.state_code})
        # sub-state
        if dbloc.feature_code in ['PPL', 'PPLA', 'PPLA2', 'ADMD', 'ISL', 'ADM2']:
            return reverse('geo:substate',
                kwargs={'continent': dbloc.continent_code, 'country': dbloc.country_code,
                        'state': dbloc.state_code, 'geonames_id': dbloc.geonames_id})
    # geonames continent
    if isinstance(dbloc, GeonamesContinent):
        return reverse('geo:continent', kwargs={'continent': dbloc.code})
    # geonames country
    if isinstance(dbloc, GeonamesCountry):
            return reverse('geo:country',
                kwargs={'continent': dbloc.continent, 'country': dbloc.code})

    # don't return 'None' for a url in the record
    return ''

@register.filter
def as_json(val):
    return mark_safe(simplejson.dumps(val))
