# file ddisearch/geo/tests.py
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

import os
from mock import patch, Mock

from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from eulxml.xmlmap import load_xmlobject_from_file
from eulexistdb import testutil as eulexistdb_testutil


from ddisearch.ddi.models import CodeBook, GeographicCoverage
from ddisearch.ddi.tests import FIXTURE_DIR
from ddisearch.geo.models import Location, GeonamesContinent, GeonamesCountry
from ddisearch.geo.geonames import GeonamesClient
from ddisearch.geo.utils import CodebookGeocoder
from ddisearch.geo.templatetags import geo_tags


class CodebookGeocoderTest(TestCase):

    fixture_filename = '02988.xml'

    mockgeonames = Mock(GeonamesClient)

    def setUp(self):
        with patch('ddisearch.geo.utils.GeonamesClient', new=self.mockgeonames):
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

        self.mockgeonames.return_value.geocode.assert_called_with(name_equals=self.cb.geo_coverage[0].val)
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
        # calls geocode to get information for inserting into the db
        self.mockgeonames.return_value.geocode.assert_called_with(feature_code='CONT',
            name_equals='Africa')
        africa = GeonamesContinent.objects.get(name='Africa')
        self.assertEqual('geonames:%s' % africa.geonames_id,
            self.cb.geo_coverage[0].id,
            'continent should have geonames id set from continent db lookup')

        # test US state logic (assume US if 3 or more states)
        del self.cb.geo_coverage[0].id
        self.cb.geo_coverage[0].val = 'California'
        self.cb.geo_coverage[1].val = 'Alaska'
        self.cb.geo_coverage.append(GeographicCoverage(val='Georgia'))
        self.cb.geo_coverage.append(GeographicCoverage(val='Puerto Rico'))
        self.mockgeonames.return_value.geocode.reset_mock()

        with patch('ddisearch.geo.utils.Location') as mockdbloc:
            mockdbloc.objects.filter.return_value.count.return_value = 0
            self.cbgeocoder.code_locations(self.cb)
            mockdbloc.objects.filter.assert_any_call(name=self.cb.geo_coverage[0].val,
                country_code='US')
            mockdbloc.objects.filter.assert_any_call(name=self.cb.geo_coverage[1].val,
                country_code='US')
            mockdbloc.objects.filter.assert_any_call(name=self.cb.geo_coverage[2].val,
                country_code='US')
            # no US for Puerto Rico
            mockdbloc.objects.filter.assert_any_call(name=self.cb.geo_coverage[3].val)
            self.mockgeonames.return_value.geocode.assert_any_call(name_equals=self.cb.geo_coverage[0].val,
                country_bias='US', admin_code1='CA')
            self.mockgeonames.return_value.geocode.assert_any_call(name_equals=self.cb.geo_coverage[1].val,
                country_bias='US', admin_code1='AK')
            self.mockgeonames.return_value.geocode.assert_any_call(name_equals=self.cb.geo_coverage[2].val,
                country_bias='US', admin_code1='GA')
            self.mockgeonames.return_value.geocode.assert_any_call(name_equals=self.cb.geo_coverage[3].val)

            # Georgia when context doesn't suggest US
            self.cb.geo_coverage[0].val = 'Romania'
            self.cb.geo_coverage[1].val = 'Ukraine'
            # 2 = Georgia, 4 = Puerto Rico
            self.mockgeonames.return_value.geocode.reset_mock()
            mockdbloc.objects.filter.return_value.count.return_value = 0
            mockdbloc.objects.filter.return_value.exclude.return_value.count.return_value = 0
            self.cbgeocoder.code_locations(self.cb)
            mockdbloc.objects.filter.assert_any_call(name='Georgia')
            # db lookup should explicitly exclude US if context doesn't suggest Georgia is a state
            mockdbloc.objects.filter.return_value.exclude.assert_any_call(country_code='US')

        # formatted names
        self.mockgeonames.return_value.geocode.reset_mock()
        self.cb.geo_coverage[0].val = 'Portland (Maine)'
        self.cb.geo_coverage[1].val = 'Hiroshima (prefecture)'
        del self.cb.geo_coverage[-1]
        del self.cb.geo_coverage[-1]
        self.cbgeocoder.code_locations(self.cb)
        self.mockgeonames.return_value.geocode.assert_any_call(name_equals='Portland',
                country_bias='US', admin_code1='ME')
        self.mockgeonames.return_value.geocode.assert_any_call(name_equals='Hiroshima')



