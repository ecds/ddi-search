import logging
import re
from django.conf import settings
from ddisearch.geo.models import Location, GeonamesCountry, GeonamesContinent
from ddisearch.geo.geonames import GeonamesClient

logger = logging.getLogger(__name__)

class CodebookGeocoder(object):
    '''Utility class to geocode the geographical coverage terms in
    a :class:`~dddisearch.ddi.models.CodeBook` in order to
    enable browsing records by geography and plotting locations on a map.
    Geographical information is stored in the database using
    :class:`~ddisearch.geo.models.Location`, and the corresponding geonames
    id is added to the xml.
    '''

    name_paren_re = re.compile('^(?P<name>[A-Z][a-zA-Z ]+) \((?P<restriction>[A-Za-z]+)\)$')

    def __init__(self):
        # initialize the geocoder for reuse
        self.geonames = GeonamesClient(username=settings.GEONAMES_USERNAME)
        # TODO: maybe also add a us-geonames initialized with a US-country
        # bias, for use when we determine we are looking at US states?
        # self.us_geonames = GeoNames(username=settings.GEONAMES_USERNAME,
        #     country_bias='US')

        # save the continents for easy lookup
        continents = GeonamesContinent.objects.all()
        self.continents = dict([(c.name, c.geonames_id) for c in continents])

    def code_locations(self, cb):
        '''Code the geographic coverage locations in a codebook'''

        # in theory this could give us some help, but is often not set
        if cb.geo_unit:
            logger.debug('geogUnit = %s' % '; '.join(cb.geo_unit))

        # FIXME: this isn't working well enough; preload state names
        # and check that some number (three?) match, then assume US?

        # check if there are at least three US states in this record,
        # to help determine if we should assume US
        us_state_count = sum([1 for geog in cb.geo_coverage if geog.val in us_states])

        # loop through geographical coverage terms and look them up,
        # setting geonames id on the geogCover element
        for geog in cb.geo_coverage:
            # for each location, don't assume US unless we have reason
            assume_US = False

            logger.info('geogCover %s' % geog.val)
            if us_state_count >= 3:
                assume_US = True

            # skip coverage of global - nothing to code
            if geog.val == 'Global':
                continue

            # special case: first check if we have a continent
            # (geonames not looking these up so well; for some reason
            # 'Europe' is geocoded as 'Minsk' and 'Africa' as 'Camayenne')
            if geog.val in self.continents:
                geog.id = 'geonames:%d' % self.continents[geog.val]

                # make sure continent is present in Locations db table
                if Location.objects.filter(name=geog.val, feature_code='CONT').count() == 0:
                    loc = self.geonames.geocode(name_equals=geog.val, feature_code='CONT')
                    dbloc = self.location_from_geoname(loc)

                continue

            geo_options = {}

            # clean names that are formatted this way:
            #   Portland (Maine)
            #   Hiroshima (prefecture)
            # if (###) is a state, use it to filter; otherwise ignore
            match = self.name_paren_re.match(geog.val)
            if match:
                matchinfo = match.groupdict()
                geogname = matchinfo['name']
                restriction = matchinfo['restriction']
                # if the parenthetical text matches a U.S. state, use that in the lookup
                if restriction in us_states:
                    assume_US = True

                # sometimes used to clarify ambiguous names, e.g. New York (state)
                elif restriction == 'state':
                    assume_US = True
                    geo_options['feature_code'] = 'ADM1'
                    # NOTE: this is the feature code for states in U.S.
                    # may need to generalize more to handle other countries
            else:
                geogname = geog.val
                restriction = None

            # next check in the db, in case we've looked up before
            country_filter = {}
            # if conditions are met where we want to assume US, restrict to
            # country code US except for Puerto Rico
            if assume_US and geogname != 'Puerto Rico':
                country_filter['country_code'] = 'US'
            db_locations = Location.objects.filter(name=geogname, **country_filter)
            # if we *don't* have reason to assume US and we get Georgia,
            # look for non-US match
            if not assume_US and geogname == 'Georgia':
                # NOTE: we could use similar logic to give a country bias to geocoder
                db_locations = db_locations.exclude(country_code='US')

            # If there is one and only one match, use it; otherwise defer to geocoder
            # to determine which place to use
            if db_locations.count() == 1:
                # store db location so we can put geonames id into the xml
                dbloc = db_locations[0]

            else:
                # use US-biased geocoder if we have hit a threshold where
                # we want to assume US (with certain exceptions)
                # FIXME: may well be others like Puerto Rico!

                if assume_US and geogname != 'Puerto Rico':
                    geo_options['country_bias'] = 'US'

                if assume_US and geogname in us_states and not restriction == 'state':
                    geo_options['admin_code1'] = us_states[geogname]
                elif restriction is not None and restriction in us_states:
                    # if we have a restriction that matches a U.S. state
                    # (e.g. "Portland (Maine"), pass that along to the geocoder
                    geo_options['admin_code1'] = us_states[restriction]

                # TODO: could be helpful to restrict by feature codes
                # to the types of entities we expect to get
                # - continents, countries, states, counties, cities
                # first try for exact match
                loc = self.geonames.geocode(name_equals=geogname, **geo_options)
                if not loc:
                    # if that doesn't work, try a looser name match
                    loc = self.geonames.geocode(name=geogname, **geo_options)
                    # if that still fails, error
                    if not loc:
                        logger.warn('No geonames result found for %s' % geogname)
                        continue
                logger.debug('geonames result: %s' % unicode(loc))
                logger.debug(loc.raw)

                # check if geonames id is already in the db
                db_locations = Location.objects.filter(geonames_id=loc.raw['geonameId'])
                if db_locations.count():
                    dbloc = db_locations[0]
                else:
                    # if not, create new db location from geonames lookup
                    dbloc = self.location_from_geoname(loc)

            # set geonames id in the xml
            geog.id = 'geonames:%d' % dbloc.geonames_id
            logger.info('setting geonames id to %s (%s, %s, %s)' % \
                        (geog.id, dbloc.name, dbloc.country_code,
                         dbloc.continent_code))


    def location_from_geoname(self, loc):
        '''Create and return a :class:`ddisearch.geo.models.Location`
        based on a location as returned by
        :class:`geopy.geocoders.GeoNames`'''

        # determine continent code based on country
        country_code = loc.raw.get('countryCode', None)
        continent_code = None
        if country_code is not None:
            try:
                c = GeonamesCountry.objects.get(code=country_code)
                continent_code = c.continent
            except:
                pass
        # special case for continents
        elif loc.raw['fcode'] == 'CONT':
            try:
                c = GeonamesContinent.objects.get(geonames_id=loc.raw['geonameId'])
                continent_code = c.code
            except:
                pass

        # get state code if there is one
        state_code = None
        admin_code = loc.raw.get('adminCode1', None)
        if admin_code and admin_code != '00':
            state_code = admin_code

        dbloc = Location(name=loc.raw['name'],
                         geonames_id=loc.raw['geonameId'],
                         latitude=loc.latitude,
                         longitude=loc.longitude,
                         country_code=country_code,
                         feature_code=loc.raw['fcode'],
                         continent_code=continent_code,
                         state_code=state_code)
        dbloc.save()

        # TODO: make sure hierarchy above location is present?
        # - continent, country, state (?)

        return dbloc


us_states = {
   'Alabama': 'AL',
   'Alaska': 'AK',
   'Arizona': 'AZ',
   'Arkansas': 'AR',
   'California': 'CA',
   'Colorado': 'CO',
   'Connecticut': 'CT',
   'Delaware': 'DE',
   'District of Columbia': 'DC',
   'Florida': 'FL',
   'Georgia': 'GA',
   'Hawaii': 'HI',
   'Idaho': 'ID',
   'Illinois': 'IL',
   'Indiana': 'IN',
   'Iowa': 'IA',
   'Kansas': 'KS',
   'Kentucky': 'KY',
   'Louisiana': 'LA',
   'Maine': 'ME',
   'Maryland': 'MD',
   'Massachusetts': 'MA',
   'Michigan': 'MI',
   'Minnesota': 'MN',
   'Mississippi': 'MS',
   'Missouri': 'MO',
   'Montana': 'MT',
   'Nebraska': 'NE',
   'Nevada': 'NV',
   'New Hampshire': 'NH',
   'New Jersey': 'NJ',
   'New Mexico': 'NM',
   'New York': 'NY',
   'North Carolina': 'NC',
   'North Dakota': 'ND',
   'Ohio': 'OH',
   'Oklahoma': 'OK',
   'Oregon': 'OR',
   'Pennsylvania': 'PA',
   'Rhode Island': 'RI',
   'South Carolina': 'SC',
   'South Dakota': 'SD',
   'Tennessee': 'TN',
   'Texas': 'TX',
   'Utah': 'UT',
   'Vermont': 'VT',
   'Virginia': 'VA',
   'Washington': 'WA',
   'West Virginia': 'WV',
   'Wisconsin': 'WI',
   'Wyoming': 'WY'
}
