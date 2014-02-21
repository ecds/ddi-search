from eulxml import xmlmap

from eulexistdb.models import XmlModel
from eulexistdb.manager import Manager

class TimePeriod(xmlmap.XmlObject):
    event = xmlmap.StringField('@event')  # start, end, single
    date = xmlmap.StringField('@date')
    cycle = xmlmap.StringField('@cycle')

class CodeBook(XmlModel):
    # NOTE: may want to adjust xpaths for effeciency when/if we query on them
    title = xmlmap.StringField('stdyDscr/citation/titlStmt/titl')
    abstract = xmlmap.StringField('.//abstract')
    # authors = xmlmap.StringListField('stdyDscr/citation/rspStmt/AuthEnty')
    authors = xmlmap.StringListField('.//AuthEnty')
    id = xmlmap.StringField('stdyDscr/citation/titlStmt/IDNo')  # possible int, but don't constrain
    id_agency = xmlmap.StringField('stdyDscr/citation/titlStmt/IDNo/@agency')

    keywords = xmlmap.StringListField('stdyDscr/stdyInfo/subject/keyword')
    topics = xmlmap.StringListField('stdyDscr/stdyInfo/subject/topcClas')

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





