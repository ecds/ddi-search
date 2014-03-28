import os
from mock import patch, Mock
from django.test import TestCase
from eulxml.xmlmap import load_xmlobject_from_file
from geopy.geocoders import GeoNames

from ddisearch.ddi.models import CodeBook
from ddisearch.ddi.tests import FIXTURE_DIR
from ddisearch.geo.models import Location, GeonamesContinent
from ddisearch.geo.utils import CodebookGeocoder

class CodebookGeocoderTest(TestCase):

    fixture_filename = '02988.xml'

    mockgeonames = Mock(GeoNames)

    def setUp(self):
        with patch('ddisearch.geo.utils.GeoNames', new=self.mockgeonames):
            self.cbgeocoder = CodebookGeocoder()

        self.cb = load_xmlobject_from_file(os.path.join(FIXTURE_DIR,
                                                        self.fixture_filename),
                                           CodeBook)

    def _mocklocation(self):
        # create & return a mock location based on what GeoNames.geocode returns
        mocklocation = Mock()
        mocklocation.latitude = 31.5
        mocklocation.longitude = 34.75
        mocklocation.raw = {
            u'fcode': u'PCLI', u'countryId': u'294640', u'name': u'Israel',
            u'countryCode': u'IL', u'geonameId': 294640, u'toponymName':
            u'State of Israel', u'fclName': u'country, state, region,...',
            u'fcodeName': u'independent political entity', u'countryName': u'Israel',
            u'lat': u'31.5', u'lng': u'34.75', u'population': 7353985, u'fcl': u'A',
            u'adminCode1': u'00', u'adminName1': ''
        }
        return mocklocation

    def test_code_locations(self):
        mocklocation = self._mocklocation()
        self.mockgeonames.return_value.geocode.return_value = mocklocation

        self.cbgeocoder.code_locations(self.cb)

        self.mockgeonames.return_value.geocode.assert_called_with(self.cb.geo_coverage[0].val)
        self.assertEqual(1, self.mockgeonames.return_value.geocode.call_count,
            'geocode should only be called once (one geogCover term and one global)')

        self.assertEqual('geonames:%s' % mocklocation.raw['geonameId'],
            self.cb.geo_coverage[0].id,
            'first geoCover (Israel) should have geonames id based on GeoNames return')
        self.assertEqual(None, self.cb.geo_coverage[1].id,
            'global geoCover should not get an id assigned')

        # delete the id and recode; should *not* do a geocoder call
        del self.cb.geo_coverage[0].id
        self.mockgeonames.return_value.geocode.reset_mock()
        self.cbgeocoder.code_locations(self.cb)
        self.assertEqual('geonames:%s' % mocklocation.raw['geonameId'],
            self.cb.geo_coverage[0].id,
            'first geoCover (Israel) should have geonames id based on db lookup')
        self.assertEqual(0, self.mockgeonames.return_value.geocode.call_count,
            'geocode should not be called when term can be found in local db')

        # special case: continent
        del self.cb.geo_coverage[0].id
        self.cb.geo_coverage[0].val = 'Africa'
        self.mockgeonames.return_value.geocode.reset_mock()
        self.cbgeocoder.code_locations(self.cb)
        self.assertEqual(0, self.mockgeonames.return_value.geocode.call_count,
            'geocode should not be called when term matches a continent')
        africa = GeonamesContinent.objects.get(name='Africa')
        self.assertEqual('geonames:%s' % africa.geonames_id,
            self.cb.geo_coverage[0].id,
            'continent should have geonames id set from continent db lookup')

        # TODO: special case test for Georgia (US state vs. country)


    def test_location_from_geoname(self):
        loc = self._mocklocation()
        self.cbgeocoder.location_from_geoname(loc)

        dbloc = Location.objects.get(geonames_id=loc.raw['geonameId'])
        self.assertEqual(dbloc.name, loc.raw['name'],
            'location name should be set from geonames raw name return')
        self.assertEqual(dbloc.geonames_id, loc.raw['geonameId'],
            'location geonames_id should be set from geonames raw return')
        self.assertEqual(dbloc.latitude, loc.latitude,
            'location latitude should be set from geonames lat return')
        self.assertEqual(dbloc.longitude, loc.longitude,
            'location longitude should be set from geonames long return')
        self.assertEqual(dbloc.feature_code, loc.raw['fcode'],
            'feature code should be set from geonames raw fcode')
        self.assertEqual(dbloc.country_code, loc.raw['countryCode'],
            'country code should be set from geonames raw return')
        self.assertEqual(dbloc.continent_code, 'AS',
            'continent code should be set from db lookup on country code')
        self.assertEqual(dbloc.state_code, None,
            'state code should not be set when adminCode1 is 00')
