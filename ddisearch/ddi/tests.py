import os
from django.conf import settings
from django.test import TestCase

from eulxml.xmlmap import load_xmlobject_from_file

from ddisearch.ddi.models import CodeBook, TimePeriod

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

