import os
from mock import patch, Mock
from geopy.geocoders import GeoNames

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from eulxml.xmlmap import load_xmlobject_from_file
from eulexistdb import testutil as eulexistdb_testutil


from ddisearch.ddi.models import CodeBook
from ddisearch.ddi.tests import FIXTURE_DIR
from ddisearch.geo.models import Location, GeonamesContinent, GeonamesCountry
from ddisearch.geo.utils import CodebookGeocoder
from ddisearch.geo.templatetags import geo_tags


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
        # make sure id is not set
        del self.cb.geo_coverage[0].id
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


class ViewsTest(eulexistdb_testutil.TestCase):
    fixtures = ['test_locations.json']
    exist_fixtures = {
        'directory': FIXTURE_DIR,
        'index': settings.EXISTDB_INDEX_CONFIGFILE  # required for fulltext search
    }
    fixture_filename = '02988.xml'

    def setUp(self):
        # load fixture xml for access to content
        self.cb = load_xmlobject_from_file(os.path.join(FIXTURE_DIR,
                                                        self.fixture_filename),
                                           CodeBook)

    def test_browse(self):
        url = reverse('geo:browse')
        response = self.client.get(url)
        self.assertContains(response, 'Asia',
            msg_prefix='browse page should list continents for which there is data')
        self.assertNotContains(response, 'Antarctica',
            msg_prefix='browse page should not list continents for which there is no data')
        self.assertContains(response, reverse('geo:continent', kwargs={'continent': 'AS'}),
            msg_prefix='browse page should link to continent page')
        self.assertContains(response, '<h2>Found <strong>1</strong> resource with Global coverage</h2>',
            html=True, msg_prefix='should display 1 resource with global coverage')
        self.assertContains(response, self.cb.title,
            msg_prefix='should display matching resource title')

    def test_browse_continent(self):
        url = reverse('geo:continent', kwargs={'continent': 'AS'})
        response = self.client.get(url)
        self.assertContains(response, 'Israel',
            msg_prefix='browse page should list countries for which there is data')
        self.assertContains(response,
            reverse('geo:country', kwargs={'continent': 'AS', 'country': 'IL'}),
            msg_prefix='browse page should link to country page')
        self.assertContains(response, 'No results found with Asia coverage',
            msg_prefix='should display no resources for with Asia coverage')
        self.assertContains(response, reverse('geo:browse'),
            msg_prefix='continent page should link up to global geography browse page')

    def test_browse_country(self):
        url = reverse('geo:country', kwargs={'continent': 'AS', 'country': 'IL'})
        response = self.client.get(url)
        # breadcrumbs
        self.assertContains(response, reverse('geo:browse'),
            msg_prefix='country page should link up to global geography browse page')
        self.assertContains(response, reverse('geo:continent', kwargs={'continent': 'AS'}),
            msg_prefix='country page should link up to parent continent page')
        self.assertContains(response, '<h2>Found <strong>1</strong> resource with Israel coverage</h2>',
            html=True, msg_prefix='should display 1 resource with global coverage')
        self.assertContains(response, self.cb.title,
            msg_prefix='should display matching resource title')


class LocationUrlTagTest(TestCase):
    fixtures = ['test_locations.json']

    def test_continent(self):
        cont = GeonamesContinent.objects.all()[0]
        self.assertEqual(reverse('geo:continent', kwargs={'continent': cont.code}),
           geo_tags.location_url(cont))

        cont = Location.objects.filter(feature_code='CONT')[0]
        self.assertEqual(reverse('geo:continent', kwargs={'continent': cont.continent_code}),
           geo_tags.location_url(cont))

    def test_country(self):
        country = GeonamesCountry.objects.all()[0]
        self.assertEqual(reverse('geo:country',
            kwargs={'continent': country.continent, 'country': country.code}),
            geo_tags.location_url(country))

        country = Location.objects.filter(feature_code='PCLI')[0]
        self.assertEqual(reverse('geo:country',
            kwargs={'continent': country.continent_code, 'country': country.country_code}),
            geo_tags.location_url(country))

    def test_state(self):
        state = Location.objects.filter(feature_code='ADM1')[0]
        self.assertEqual(reverse('geo:state',
            kwargs={'continent': state.continent_code, 'country': state.country_code,
                    'state': state.state_code}),
            geo_tags.location_url(state))

    def test_substate(self):
        substate = Location.objects.filter(feature_code='PPLA2')[0]
        self.assertEqual(reverse('geo:substate',
            kwargs={'continent': substate.continent_code, 'country': substate.country_code,
                    'state': substate.state_code, 'geonames_id': substate.geonames_id}),
            geo_tags.location_url(substate))

