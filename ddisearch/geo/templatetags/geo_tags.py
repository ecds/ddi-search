from django import template
from django.core.urlresolvers import reverse
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
        # country-level
        if dbloc.feature_code.startswith('PCL'):
            return reverse('geo:country',
                kwargs={'continent': dbloc.continent_code, 'country': dbloc.country_code})
        # state
        if dbloc.feature_code == 'ADM1':
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
