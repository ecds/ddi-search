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

class Date(xmlmap.XmlObject):
    'XML model for a DDI date (e.g., time period or collection date)'
    #: **start** or **end** if date is part or a range; **single** if not
    event = xmlmap.StringField('@event')  # start, end, single
    #: actual date value
    date = xmlmap.StringField('@date')
    #: identifier for cycle of date ranges; used to group related start and end dates
    cycle = xmlmap.StringField('@cycle')
    #: text content of the date, if any (e.g., collection date label)
    label = xmlmap.StringField('text()')

    def __unicode__(self):
        return self.label

class Version(xmlmap.XmlObject):
    'XML model for a DDI version in the document version statement'
    #: actual date value
    date = xmlmap.DateField('@date')
    # could also have source and type attirbutes...

    def __unicode__(self):
        return self.date

class Nation(xmlmap.XmlObject):
    'XML model for a DDI nation'
    #: full name of the nation
    val = xmlmap.StringField('text()')
    #: abbreviated name (may be ISO country code)
    abbr = xmlmap.StringField('@abbr')

    def __unicode__(self):
        return self.val


class CodeBook(XmlModel):
    '''XML model for interacting with a single Data Dcoument Initiative (DDI)
    CodeBook document.

    For more information on DDI, see the `DDI Alliance`_ website.

    For technical information, refer to the list of `"DDI-Lite" recommended elements`_ or
    `field-level documentation`_.

.. _DDI Alliance: http://www.ddialliance.org/
.. _"DDI-Lite" recommended elements: http://www.ddialliance.org/sites/default/files/ddi-lite.html
.. _field-level documentation: http://www.ddialliance.org/Specification/DDI-Codebook/2.5/XMLSchema/field_level_documentation.html

    '''
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
    #: time periods covered by the data, as a list of :class:`Date`.
    #:
    #: **Recommended:** use the :attr:`dates` property for display, which collects
    #: range and single dates into a list of dates and date ranges.
    time_periods = xmlmap.NodeListField('.//timePrd', Date)
    #: dates when data were collected; list of :class:`Date`
    collection_dates = xmlmap.NodeListField('stdyDscr/stdyInfo/sumDscr/collDate', Date)
    #: list of nations as :class:`Nation`
    nations = xmlmap.NodeListField('stdyDscr/stdyInfo/sumDscr/nation', Nation)
    #: list of terms indicating the geographical coverage or scope of the data
    geo_coverage = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/geogCover')
    #: list of terms indicating the unit of analysis
    analysis_unit = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/anlyUnit')
    #: list of terms describing the person or elements that are the object of research
    universe = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/universe')
    #: list of terms describing the kind of data
    kind_of_data = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/dataKind')
    #: list of notes fields, which may contain other details about the study
    study_notes = xmlmap.StringListField('stdyDscr/stdyInfo/notes')

    # technically probably a datefield; could be 4 digit year, or YYYY-MM
    # full xpath is stdyDscr/stdyInfo/sumDscr
    # XPath for sorting by date; sort on the earliest date available (single or date range)
    sort_date_xpath = 'min(%(xq_var)s//timePrd/string(@date))'

    #: document version, as an instance of :class:`Version`
    #: intended for use in identifying new additions
    document_version = xmlmap.NodeField('docDscr//verStmt/version', Version)

    #: boosted fields in the index that should be searched to get a tuned
    #: relevance score - titl, abstract, geogCover
    boostfields = xmlmap.StringField('.//titl | .//abstract | .//geogCover')

    #: geographical fields to be used in "location" search:
    #: geogCover, nation, universe
    location = xmlmap.StringField('.//geogCover | .//nation | .//universe')

    objects = Manager('/codeBook')

    @property
    def dates(self):
        '''Dynamic property to generate a list of dates and/or date ranges
        associated with this dataset.

        Iterates through all the :attr:`time_periods` and groups any start/end
        dates for the same cycle to generate a list of dates or date ranges
        that can easily be displayed.

        :rtype: list
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





