import os
from copy import copy
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import TestCase

from eulxml.xmlmap import load_xmlobject_from_file
from eulexistdb import testutil as eulexistdb_testutil

from ddisearch.ddi.models import CodeBook, TimePeriod
from ddisearch.ddi.forms import KeywordSearch

FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')


class CodeBookTest(TestCase):

    def setUp(self):
        self.cb = load_xmlobject_from_file(os.path.join(FIXTURE_DIR, '02988.xml'),
                                           CodeBook)

    def test_properties(self):
        self.assertEqual('Israeli Election Study, 1973', self.cb.title)
        self.assert_(self.cb.abstract.startswith('This study is one in a series of election studies conducted since 1969 by Alan Arian'))
        self.assertEqual(2, len(self.cb.authors))
        self.assert_('Arian, Asher' in self.cb.authors)
        self.assert_('Turgovnik, Ephraim' in self.cb.authors)
        self.assertEqual(35, len(self.cb.keywords))
        self.assert_('Arab Israeli conflict' in self.cb.keywords)
        self.assert_('social attitudes' in self.cb.keywords)
        self.assertEqual(4, len(self.cb.topics))
        self.assert_('Mass Political Behavior and Attitudes' in self.cb.topics[0])
        self.assertEqual(5, len(self.cb.time_periods))
        self.assert_(isinstance(self.cb.time_periods[0], TimePeriod))
        self.assertEqual('single', self.cb.time_periods[0].event)
        self.assertEqual('1973', self.cb.time_periods[0].date)
        self.assertEqual('P1', self.cb.time_periods[0].cycle)
        self.assertEqual('start', self.cb.time_periods[1].event)

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
        response = self.client.get(search_url)
        self.assert_('form' in response.context)
        self.assert_(isinstance(response.context['form'], KeywordSearch))
        # validation error when no search terms are entered
        self.assertContains(response, 'enter search terms for at least one of')

        # keyword search
        response = self.client.get(search_url,
            {'per_page': 10, 'sort': 'relevance', 'keyword' : 'israeli election'})

        # basic tests for template display of search result
        self.assertContains(response, 'Found <strong>1</strong> result.',
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
