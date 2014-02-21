from eulxml import xmlmap

from eulexistdb.models import XmlModel
from eulexistdb.manager import Manager

class IDNumber(xmlmap.XmlObject):
    'XML model for DDI codebook IDNo'
    #: id value
    val = xmlmap.StringField('text()')
    #: id agency
    agency = xmlmap.StringField('@agency')

    def __unicode__(self):
        return self.val

class TimePeriod(xmlmap.XmlObject):
    'XML model for a time period in a DDI codebook'
    #: **start** or **end** if date is part or a range; **single** if not
    event = xmlmap.StringField('@event')  # start, end, single
    #: actual date value
    date = xmlmap.StringField('@date')
    #: identifier for cycle of date ranges; used to group related start and end dates
    cycle = xmlmap.StringField('@cycle')


class CodeBook(XmlModel):
    '''XML model for interacting with a single DDI CodeBook document.'''
    # NOTE: may want to adjust xpaths for effeciency when/if we query on them

    #: title for the study
    title = xmlmap.StringField('stdyDscr/citation/titlStmt/titl')
    #: study abstract
    abstract = xmlmap.StringField('.//abstract')
    #: list of authors
    authors = xmlmap.StringListField('.//AuthEnty')
    #: id information, via :class:`IDNumber`
    id = xmlmap.NodeField('stdyDscr/citation/titlStmt/IDNo', IDNumber)
    #: list of keywords
    keywords = xmlmap.StringListField('stdyDscr/stdyInfo/subject/keyword')
    #: list of topics
    topics = xmlmap.StringListField('stdyDscr/stdyInfo/subject/topcClas')
    #: list of :class:`TimePeriod` elements
    time_periods = xmlmap.NodeListField('.//timePrd', TimePeriod)

    # technically probably a datefield; could be 4 digit year, or YYYY-MM
    # full xpath is stdyDscr/stdyInfo/sumDscr
    # XPath for sorting by date; sort on the earliest date available (single or date range)
    sort_date_xpath = 'min(%(xq_var)s//timePrd/string(@date))'

    # boosted fields in the index that should be searched to get a tuned
    # relevance score
    boostfields = xmlmap.StringField('.//titl | .//abstract | .//geogCover')

    objects = Manager('/codeBook')

    @property
    def dates(self):
        '''List of dates or date ranges associated with this dataset.

        Iterates through all the timePrd elements and groups any start/end
        dates for the same cycle to generate a list of dates or date ranges
        that can easily be displayed.
        '''
        dates = []
        start = {}
        for t in self.time_periods:
            if t.event == 'single':
                dates.append(t.date)
            elif t.event == 'start':
                start[t.cycle] = t.date
            elif t.event == 'end':
                if t.cycle in start:
                    # FIXME: how best to display two dates when date could
                    # be year or year-month-day ?
                    sep = '-'
                    if '-' in start[t.cycle] or '-' in t.date:
                        sep = ' - '
                    dates.append('%s%s%s' % (start[t.cycle], sep, t.date))

        return dates





