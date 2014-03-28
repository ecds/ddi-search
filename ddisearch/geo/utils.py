import logging
from django.conf import settings
from geopy.geocoders import GeoNames
from ddisearch.geo.models import Location, GeonamesCountry, GeonamesContinent

logger = logging.getLogger(__name__)

class CodebookGeocoder(object):
    '''Utility class to geocode the geographical coverage terms in
    a :class:`~dddisearch.ddi.models.CodeBook` in order to
    enable browsing records by geography and plotting locations on a map.
    Geographical information is stored in the database using
    :class:`~ddisearch.geo.models.Location`, and the corresponding geonames
    id is added to the xml.
    '''

    def __init__(self):
        # initialize the geocoder for reuse
        self.geonames = GeoNames(username=settings.GEONAMES_USERNAME)
        # TODO: maybe also add a us-geonames initialized with a US-country
        # bias, for use when we determine we are looking at US states?

        # save the continents for easy lookup
        continents = GeonamesContinent.objects.all()
        self.continents = dict([(c.name, c.geonames_id) for c in continents])

    def code_locations(self, cb):
        '''Code the geographic coverage locations in a codebook'''

        # in theory this could give us some help, but is often not set
        if cb.geo_unit:
            logger.debug('geog unit = %s' % '; '.join(cb.geo_unit))

        # loop through geographical coverage terms and look them up,
        # setting geonames id on the geogCover element
        for geog in cb.geo_coverage:
            logger.info(geog.val)

            # skip coverage of global - nothing to code
            if geog.val == 'Global':
                continue

            # special case: first check if we have a continent
            # (geonames not looking these up so well; for some reason
            # 'Europe' is geocoded as 'Minsk' and 'Africa' as 'Camayenne')
            if geog.val in self.continents:
                geog.id = 'geonames:%d' % self.continents[geog.val]
                # NOTE: this *doesn't* put a record in the Locations db;
                # should be ok because other records will account for that (?)
                continue

            # next check in the db, in case we've looked up before
            db_locations = Location.objects.filter(name=geog.val)
            # FIXME: logic to handle Georgia here
            if db_locations.count():
                # store db location so we can put geonames id into the xml
                dbloc = db_locations[0]

            else:
                loc = self.geonames.geocode(geog.val)
                if not loc:
                    print 'no match found for %s' % geog.val
                    continue
                logger.debug(unicode(loc))
                logger.debug(loc.raw)

                # TODO: extra logic for interpreting Georgia as state/country?
                # if locations include US and any US states, should be state
                # if locations include US and other countries, should be country

                # similar case for Montana (BG?) and Florida (UY?)
                # possibly affecting other states as well

                # check if geonames id is already in the db
                db_locations = Location.objects.filter(geonames_id=loc.raw['geonameId'])
                if db_locations.count():
                    dbloc = db_locations[0]
                else:
                    # if not, create new db location from geonames lookup
                    dbloc = self.location_from_geoname(loc)


            # set geonames id in the xml
            geog.id = 'geonames:%d' % dbloc.geonames_id
            logger.info('setting geonames id to %s' % geog.id)


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

