import os
from copy import copy
import datetime
import shutil
from StringIO import StringIO
import tempfile
from mock import patch

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.management.base import CommandError
from django.test import TestCase
from django.test.utils import override_settings

from eulxml.xmlmap import load_xmlobject_from_file
from eulexistdb import testutil as eulexistdb_testutil
from eulexistdb.db import ExistDB

from ddisearch.ddi.models import CodeBook, Date, IDNumber, Nation
from ddisearch.ddi.forms import KeywordSearch
from ddisearch.ddi.management.commands import load

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class CodeBookTest(TestCase):

    def setUp(self):
        self.cb = load_xmlobject_from_file(os.path.join(FIXTURE_DIR, '02988.xml'),
                                           CodeBook)

    def test_properties(self):
        self.assertEqual('Israeli Election Study, 1973', self.cb.title)
        self.assert_(self.cb.abstract.startswith('This study is one in a series of election studies conducted since 1969 by Alan Arian'))
        self.assert_(isinstance(self.cb.id, IDNumber))
        self.assertEqual("2988", self.cb.id.val)
        self.assertEqual("ICPSR", self.cb.id.agency)
        self.assertEqual(2, len(self.cb.authors))
        self.assert_('Arian, Asher' in self.cb.authors)
        self.assert_('Turgovnik, Ephraim' in self.cb.authors)
        self.assertEqual(35, len(self.cb.keywords))
        self.assert_('Arab Israeli conflict' in self.cb.keywords)
        self.assert_('social attitudes' in self.cb.keywords)
        self.assertEqual(4, len(self.cb.topics))
        self.assert_('Mass Political Behavior and Attitudes' in self.cb.topics[0])
        # time periods
        self.assertEqual(5, len(self.cb.time_periods))
        self.assert_(isinstance(self.cb.time_periods[0], Date))
        self.assertEqual('single', self.cb.time_periods[0].event)
        self.assertEqual('1973', self.cb.time_periods[0].date)
        self.assertEqual('P1', self.cb.time_periods[0].cycle)
        self.assertEqual('start', self.cb.time_periods[1].event)
        # collection dates
        self.assertEqual(7, len(self.cb.collection_dates))
        self.assert_(isinstance(self.cb.collection_dates[0], Date))
        self.assertEqual('single', self.cb.collection_dates[0].event)
        self.assertEqual('1973-05', self.cb.collection_dates[0].date)
        self.assertEqual('P1', self.cb.collection_dates[0].cycle)
        self.assertEqual('First pre-war', self.cb.collection_dates[0].label)
        # nations
        self.assertEqual(1, len(self.cb.nations))
        self.assert_(isinstance(self.cb.nations[0], Nation))
        self.assertEqual('Please see geographic coverage.', self.cb.nations[0].val)
        # geo coverage
        self.assertEqual(2, len(self.cb.geo_coverage))
        self.assertEqual('Israel', self.cb.geo_coverage[0])
        self.assertEqual('Global', self.cb.geo_coverage[1])

        self.assertEqual('individual', self.cb.analysis_unit[0])
        self.assert_(self.cb.universe[0].startswith('Urban adult Jewish population'))
        self.assertEqual('survey data', self.cb.kind_of_data[0])

    def test_dates(self):
        dates = self.cb.dates
        # one single date and two sets of date ranges
        self.assertEqual(3, len(dates))
        self.assertEqual('1973', dates[0])  # single date
        self.assertEqual('1974-01-13 - 1974-01-15', dates[1])
        self.assertEqual('1973-12-19 - 1973-12-20', dates[2])


class KeywordSearchTest(TestCase):
    # test keyword search form class

    def test_validation(self):
        # no terms - invalid
        form = KeywordSearch({})
        self.assertFalse(form.is_valid())
        # no search terms - invalid
        req_opts = {'sort': 'relevance', 'per_page': 10}
        form = KeywordSearch(req_opts)
        self.assertFalse(form.is_valid())
        # any single search term - valid
        opts = copy(req_opts)
        opts.update({'keyword': 'term'})
        self.assertTrue(KeywordSearch(opts).is_valid())
        opts = copy(req_opts)
        opts.update({'title': 'term'})
        self.assertTrue(KeywordSearch(opts).is_valid())
        opts = copy(req_opts)
        opts.update({'summary': 'term'})
        self.assertTrue(KeywordSearch(opts).is_valid())
        opts = copy(req_opts)
        opts.update({'source': 'term'})
        self.assertTrue(KeywordSearch(opts).is_valid())
        # all search terms is also valid
        opts.update({'keyword': 'term1', 'title': 'term2', 'summary': 'term3', 'source': 'term4'})
        self.assertTrue(KeywordSearch(opts).is_valid())

    def test_all_search_terms(self):
        opts = {'sort': 'relevance', 'per_page': 10}
        form = KeywordSearch(opts)
        # form.is_valid()  # validation required to get search terms
        self.assertEqual('', form.all_search_terms)
        opts['keyword'] = 'horse presidential'
        form = KeywordSearch(opts)
        form.is_valid()
        self.assertEqual(opts['keyword'], form.all_search_terms)
        opts.update({'title': '1973', 'source': 'michigan'})
        form = KeywordSearch(opts)
        form.is_valid()
        self.assertEqual(' '.join([opts['keyword'], opts['title'], opts['source']]),
            form.all_search_terms)
        opts.update({'summary': 'election'})
        form = KeywordSearch(opts)
        form.is_valid()
        self.assertEqual(' '.join([opts['keyword'], opts['title'], opts['summary'], opts['source']]),
            form.all_search_terms)


class ViewsTest(eulexistdb_testutil.TestCase):
    exist_fixtures = {
        'directory': FIXTURE_DIR,
        'index': settings.EXISTDB_INDEX_CONFIGFILE  # required for fulltext search
    }

    def setUp(self):
        # load fixture xml for access to content
        self.cb = load_xmlobject_from_file(os.path.join(FIXTURE_DIR, '02988.xml'),
                                           CodeBook)

    def test_search(self):
        # no search terms
        search_url = reverse('ddi:search')
        response = self.client.get(search_url, {'keyword': ''})
        self.assert_('form' in response.context)
        self.assert_(isinstance(response.context['form'], KeywordSearch))
        # validation error when no search terms are entered
        self.assertContains(response, 'enter search terms for at least one of')

        # keyword search
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election'})

        # basic tests for template display of search result
        self.assertContains(response, 'Found <strong>1</strong> resource',
            msg_prefix='response should indicate number of matches found')
        self.assertContains(response, self.cb.title,
            msg_prefix='response should include title for matching document')
        self.assertContains(response, self.cb.abstract[:50],
            msg_prefix='response should include beginning of abstract for matching document')
        self.assertContains(response, 'Principal Investigators:',
            msg_prefix='response should include principal investigators section when present')
        self.assertContains(response, self.cb.authors[0],
            msg_prefix='response should include principal investigator when present')
        self.assertContains(response, self.cb.keywords[0],
            msg_prefix='response should include keywords when present (first keyword)')
        self.assertContains(response, self.cb.keywords[1],
            msg_prefix='response should include keywords when present (second keyword)')
        self.assertContains(response, '; '.join(self.cb.dates),
            msg_prefix='response should include document dates')

        # title search
        # - matches fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'title' : 'israeli election 1973'})
        self.assertEqual(1, response.context['results'].paginator.count)
        # - does not match fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'title' : 'horse'})
        self.assertEqual(0, response.context['results'].paginator.count)
        # abstract search
        # - matches fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'summary' : 'voting patterns Arab-Israeli conflict'})
        self.assertEqual(1, response.context['results'].paginator.count)
        # - does not match fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'summary' : 'horse'})
        self.assertEqual(0, response.context['results'].paginator.count)
        # source search
        # - matches fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'source' : 'asher'})
        self.assertEqual(1, response.context['results'].paginator.count)
        # - does not match fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'source' : 'horse'})
        self.assertEqual(0, response.context['results'].paginator.count)
        # location search
        # - matches fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'location' : 'israel'})
        self.assertEqual(1, response.context['results'].paginator.count,
            'expected 1 result for search on location:israel')
        # - does not match fixture
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'location' : 'brazil'})
        self.assertEqual(0, response.context['results'].paginator.count,
            'expected no results for search on location:brazil')

        # combined fields - match
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'title': 'israeli',
             'summary': 'voting', 'source' : 'asher'})
        self.assertEqual(1, response.context['results'].paginator.count)
        # - no match
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'title': 'israeli',
             'summary': 'voting', 'source' : 'horse'})
        self.assertEqual(0, response.context['results'].paginator.count)

    def test_search_by_date(self):
        search_url = reverse('ddi:search')

        # single date - partial date match in the fixture (1974-01-15)
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'start_date': 1974, 'end_date': 1974})
        self.assertEqual(1, response.context['results'].paginator.count,
            'expected one result from date search on 1974')
        # single date that does not match
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'start_date': 1975, 'end_date': 1975})
        self.assertEqual(0, response.context['results'].paginator.count,
            'expected no results from date search on 1975')
        # after date
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'start_date': 1960})
        self.assertEqual(1, response.context['results'].paginator.count,
            'expected one result from date search on items after 1960')
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'start_date': 1980})
        self.assertEqual(0, response.context['results'].paginator.count,
            'expected no results from date search on items after 1980')
        # before date
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'end_date': 1974})
        self.assertEqual(1, response.context['results'].paginator.count,
            'expected one result from date search on items before 1974')
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'end_date': 1972})
        self.assertEqual(0, response.context['results'].paginator.count,
            'expected no results from date search on items before 1972')
        # date range
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'start_date': 1960, 'end_date': 2000})
        self.assertEqual(1, response.context['results'].paginator.count,
            'expected one result from date search on items from 1960-2000')
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election',
            'start_date': 1960, 'end_date': 1972})
        self.assertEqual(0, response.context['results'].paginator.count,
            'expected no results from date search on items from 1960-1972')

    def test_resource(self):
        # single document display
        resource_url = reverse('ddi:resource',
            kwargs={'id': self.cb.id, 'agency': self.cb.id.agency })
        response = self.client.get(resource_url)
        self.assertContains(response, '<h1>%s</h1>' % self.cb.title,
            html=True)
        for author in self.cb.authors:
            self.assertContains(response, author)
        # check subset of keyword terms
        for i in range(10):
            self.assertContains(response, self.cb.keywords[i])
        # just test for part of the abstract (full thing too long for comparison)
        self.assertContains(response, '<p>%s' % self.cb.abstract[:150])
        self.assertContains(response, '%s</p>' % self.cb.abstract[-150:])

        # bogus id should 404
        resource_url = reverse('ddi:resource',
            kwargs={'id': '12345678', 'agency': self.cb.id.agency })
        response = self.client.get(resource_url)
        expected, got = 404, response.status_code
        self.assertEqual(expected, got,
            'expected status code %s for %s with bogus id, got %s' % \
            (expected, resource_url, got))


class LoadCommandTest(TestCase):
    testfile = os.path.join(FIXTURE_DIR, '02988.xml')



    def setUp(self):
        self.cmd = load.Command()
        self.cmd.stdout = StringIO()
        self.db = ExistDB()
        self._exist_content = []

    def tearDown(self):
        # remove any tempfiles loaded to exist
        for f in self._exist_content:
            self.db.removeDocument(f)

    def test_errors(self):

        # config error
        with override_settings(EXISTDB_ROOT_COLLECTION=''):
            self.assertRaises(CommandError, self.cmd.handle)

        # invalid file error
        self.cmd.handle('/tmp/notarealfile.xml')
        self.assert_('Error opening' in self.cmd.stdout.getvalue())

    def test_load(self):
        tmp = tempfile.NamedTemporaryFile(suffix='.xml', delete=False)
        # delete false to avoid error, since the script will remove
        shutil.copyfile(self.testfile, tmp.name)

        self.cmd.handle(tmp.name)

        # check that document was loaded to exist
        exist_path = '%s/%s' % (settings.EXISTDB_ROOT_COLLECTION,
                                os.path.basename(tmp.name))
        desc = self.db.describeDocument(exist_path)
        self.assert_(desc,
            'document description should be non-empty for loaded content')
        self._exist_content.append(exist_path)  # queue for removal in cleanup
        mod = desc['modified']
        self.assertEqual(datetime.date(mod.year, mod.month, mod.day),
            datetime.date.today(),
            'loaded document should show modification date of today')
        # check file was removed
        self.assertFalse(os.path.exists(tmp.name),
            'local copy of file should be deleted after loaded to eXist')

    def test_load_remove_error(self):
        # simulate error removing local copy of file
        tmp = tempfile.NamedTemporaryFile(suffix='.xml')
        shutil.copyfile(self.testfile, tmp.name)

        # simulate deletion error
        with patch('ddisearch.ddi.management.commands.load.os.remove') as mockremove:
            mockremove.side_effect = OSError('Permission Denied')
            self.cmd.handle(tmp.name)

        cmd_output = self.cmd.stdout.getvalue()
        self.assert_('Error removing ' in cmd_output,
            'script should report when there is an error removing local file')
        self.assert_('Permission Denied' in cmd_output)

        # queue for removal in cleanup
        exist_path = '%s/%s' % (settings.EXISTDB_ROOT_COLLECTION,
                                os.path.basename(tmp.name))
        self._exist_content.append(exist_path)

