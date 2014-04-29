import re
from django.conf import settings
from django.db.models import Q
# NOTE: using django SortedDict instaed of collections.OrderedDict to support py2.7
from django.utils.datastructures import SortedDict
from eulxml import xmlmap

from eulexistdb.models import XmlModel
from eulexistdb.manager import Manager

from ddisearch.geo.models import Location, StateCode, GeonamesCountry

### top-level info and descriptive information about the study

class IDNumber(xmlmap.XmlObject):
    'XML model for DDI codebook IDNo'
    #: id value
    val = xmlmap.StringField('text()')
    #: id agency
    agency = xmlmap.StringField('@agency')

    def __unicode__(self):
        return self.val


class Version(xmlmap.XmlObject):
    'XML model for a DDI version in the document version statement'
    #: actual date value; mapping as string instead of date field because
    #: of variable date formatting (YYYY-MM-DD vs. just YYYY-MM)
    date = xmlmap.StringField('@date')
    # could also have source and type attributes...

    def __unicode__(self):
        return self.date


class Author(xmlmap.XmlObject):
    'XML model for DDI codebook Authoring Entity'
    #: name of the person or organization
    text = xmlmap.StringField('text()')
    #: author affiliation (optional)
    affiliation = xmlmap.StringField('@affiliation')

    def __unicode__(self):
        return self.text


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


class Producer(Author):
    '''Producer in the :class:`ProductionStatement`; inherits
    :attr:`text`, attr:`affiliation`, and unicode method from :class:`Author`'''
    #: abbreviation (optional)
    abbr = xmlmap.StringField('@abbr')
    #: role (optional)
    role = xmlmap.StringField('@role')


class ProductionStatement(xmlmap.XmlObject):
    '''Production statement (prodStmt) section of a DDI Codebook

    Not currently mapped: production place, software, grantNo
    '''
    #: list of producers, if any, as :class:`Producer`
    producers = xmlmap.NodeListField('producer', Producer)
    #: copyright statement
    copyright = xmlmap.StringField('copyright')
    #: production date or dates; list of :class:`Date`
    dates = xmlmap.NodeListField('date', Date)
    #: funding agencies or sponsors
    #: (mapping as string, but could have role or abbreviation attributes)
    funding_agencies = xmlmap.StringListField('fundAg')

class Abstract(xmlmap.XmlObject):
    #: direct text of the abstract (no subtags)
    txt = xmlmap.StringField('text()')
    #: list of paragraphs for abstracts that contain nested tags
    p = xmlmap.StringListField('p')

    def __unicode__(self):
        return self.txt


class Nation(xmlmap.XmlObject):
    'XML model for a DDI nation'
    #: full name of the nation
    val = xmlmap.StringField('text()')
    #: abbreviated name (may be ISO country code)
    abbr = xmlmap.StringField('@abbr')

    def __unicode__(self):
        return self.val

class GeographicCoverage(xmlmap.XmlObject):
    'XML model for geographical coverae (DDI geogCover)'
    ROOT_NAME = 'geogCover'
    #: full name of the place
    val = xmlmap.StringField('text()')
    #: xml id
    id = xmlmap.StringField('@id')

    def __unicode__(self):
        return self.val


    #: list of terms indicating the geographical coverage or scope of the data
    geo_coverage = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/geogCover')

class Topic(xmlmap.XmlObject):
    'XML model for topcClas'
    ROOT_NAME = 'topcClas'
    #: text value of the topic
    val = xmlmap.StringField('text()')
    #: source
    source = xmlmap.StringField('@source')
    #: vocabulary
    vocab = xmlmap.StringField('@vocab')

    def __unicode__(self):
        return self.val


## methodology section

class SourceStatement(xmlmap.XmlObject):
    '''description of sources used for :class:`DataCollection`

    **NOTE:** sources could be recursive; currently not mapped.'''
    #: data sources (books, articles, etc)
    data_sources = xmlmap.StringListField('dataSrc')
    #: information about origin of sources
    origins = xmlmap.StringListField('srcOrig')
    #: characteristics & quality of source material
    characteristics = xmlmap.StringListField('srcChar')
    #: documentation & access of sources
    #: (could be repeated for multiple languages; only first mapped)
    documentation = xmlmap.StringField('srcDocu')


class DataCollection(xmlmap.XmlObject):
    '''data collection methodology

    Not mapped: actMin, ConOps
    '''
    #: time method or dimension of data collection (`timeMeth`)
    time_methods = xmlmap.StringListField('timeMeth')
    #: entities responsible for collecting the data (`dataCollector`)
    collectors = xmlmap.StringListField('dataCollector')
    #: frequency of collection (`frequenc`)
    frequency = xmlmap.StringListField('frequenc')
    #: sampling procedure for selecting participants (`sampProc`)
    sample_proc = xmlmap.StringListField('sampProc')
    #: deviations from sample design (`deviat`)
    deviations = xmlmap.StringListField('deviat')
    #: methods used to collect the data (`collMode`)
    methods = xmlmap.StringListField('collMode')
    #: type of data collection instruments usede (`resInstru`)
    research_instruments = xmlmap.StringListField('resInstru')
    #: description of sources used for data collection (`sources`),
    #: list of :class:`SourceStatement`
    sources = xmlmap.NodeListField('sources', SourceStatement)
    #: noteworthy aspects of data collection situation (`collSitu`)
    situation = xmlmap.StringListField('collSitu')
    #: criteria for using weights in analysis of a collection (`weight`)
    weights = xmlmap.StringListField('weight')
    #: methods used to clean the data for consistency, etc. (`cleanOps`)
    cleaning = xmlmap.StringListField('cleanOps')


class Method(xmlmap.XmlObject):
    'Methodology and processing'
    #: list of data collection sections (`dataColl`), as instance of
    #: :class:`DataCollection`
    data_collection = xmlmap.NodeListField('dataColl', DataCollection)
    #: list of notes (`notes`)
    notes = xmlmap.StringListField('notes')
    #: response rates; could be broader description or related info
    #: (`anlyInfo/respRate`)
    response_rates = xmlmap.StringListField('anlyInfo/respRate')
    #: information on sample estimates and precision
    #: ('anlyInfo/EstSmpErr')
    sample_error_estimates = xmlmap.StringListField('anlyInfo/EstSmpErr')
    #: other issues pertaining to data appraisal (`anlyInfo/dataAppr`)
    data_appraisail = xmlmap.StringListField('anlyInfo/dataAppr')

### data access and availability section

class DataAvailability(xmlmap.XmlObject):
    'information about data availability'
    #: media (e.g.online)
    media = xmlmap.StringField('@media')
    #: access place - location of the data collection
    access_place = xmlmap.StringField('accsPlac')
    #: URI associated with :attr:`access_place`
    access_uri = xmlmap.StringField('accsPlac/@URI')
    #: availability status
    status = xmlmap.StringListField('avlStatus')
    #: extent of collection, or number & type of files
    collection_size = xmlmap.StringListField('collSize')
    #: number of files in the collection
    file_quantity = xmlmap.StringListField('fileQnty')
    #: notes
    notes = xmlmap.StringListField('notes')

class UseStatement(xmlmap.XmlObject):
    '''More information about terms of use for the data

    Not currently mapped: confidentiality declaration, contact,
    citation requirement, deposit requirement

    '''
    #: text describing any special permissions required to access the resource
    special_perms = xmlmap.StringField('specPerm')
    #: text describing restrictions on access or use of the collection
    restriction = xmlmap.StringField('restrctn')
    #: additional information about conditions of access and use;
    #: **NOTE:** may contain HTML tags
    conditions = xmlmap.StringField('conditions')
    #: disclaimer regarding responsibility of use
    #: (could be repeated to support multiple languages; only mapping first)
    disclaimer = xmlmap.StringField('disclaimer')

class DataAccess(xmlmap.XmlObject):
    'Data Access (dataAccs) section of the DDI Codebook'
    #: information about dataset availability
    availability = xmlmap.NodeListField('setAvail', DataAvailability)
    #: information on terms of use; could be repeated to support multiple
    #: languages (currently only mapping the first)
    use = xmlmap.NodeField('useStmt', UseStatement)
    #: notes
    notes = xmlmap.StringListField('notes')

## file description section

class DataFile(xmlmap.XmlObject):
    '''A single file in a :class:`FileDescription`.

    Not mapped: fileStrc (file structure), dimensions, format, place of
    file production, data checks, processing status, missing data,
    software, version statement
    '''
    #: id
    id = xmlmap.StringField('@ID')
    #: name or short title
    name = xmlmap.StringField('fileName')
    #: description of the file
    contents = xmlmap.StringField('fileCont')
    #: type of file
    type = xmlmap.StringField('fileType')


class FileDescription(xmlmap.XmlObject):
    '''Information about the data files in a collection.

    Not mapped: location map (physical storage locations)
    '''
    #: id
    id = xmlmap.StringField('@ID')
    #: list of individual files, as :class:`DataFile`
    files = xmlmap.NodeListField('fileTxt', DataFile)
    #: notes
    notes = xmlmap.StringListField('notes')


### top-level document

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
    #: study subtitle
    subtitle = xmlmap.StringField('stdyDscr/citation/titlStmt/subTitl')
    #: alternate title
    alt_title = xmlmap.StringField('stdyDscr/citation/titlStmt/altTitl')
    #: id information, via :class:`IDNumber`
    id = xmlmap.NodeField('stdyDscr/citation/titlStmt/IDNo', IDNumber)
    #: version information for the study, as :class:`Version`
    version = xmlmap.NodeField('stdyDscr/citation/verStmt/version', Version)
    #: any notes associated with the version statement
    version_notes = xmlmap.StringListField('stdyDscr/citation/verStmt/notes', Version)
    #: study abstract
    abstract = xmlmap.StringField('.//abstract')
    #: list of all abstract fields
    abstract_list = xmlmap.NodeListField('.//abstract', Abstract)
    #: bibligraphic citation
    bibligraphic_citation = xmlmap.StringField('stdyDscr/citation/biblCit')

    #: list of authors, as :class:`Author`
    authors = xmlmap.NodeListField('stdyDscr//AuthEnty', Author)
    #: list of keywords
    keywords = xmlmap.StringListField('.//keyword')
    # keywords = xmlmap.StringListField('stdyDscr/stdyInfo/subject/keyword')

    #: list of topics
    topics = xmlmap.NodeListField('stdyDscr/stdyInfo/subject/topcClas', Topic)
    # NOTE: full path is needed to allow adding local topics when loading to eXist
    # xpath .//topcClas might be more efficient for searching

    #: list of local topics (generalized local set derived from ICPSR terms)
    #: NOTE: terminology/variable name could change
    local_topics = xmlmap.NodeListField('.//topcClas[@vocab="local"]', Topic)

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
    geo_coverage = xmlmap.NodeListField('stdyDscr/stdyInfo/sumDscr/geogCover', GeographicCoverage)
    #: description of the lowest level of geographical unit in :attr:`geo_coverage`
    geo_unit = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/geogUnit')
    #: list of terms indicating the unit of analysis
    analysis_unit = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/anlyUnit')
    #: list of terms describing the person or elements that are the object of research
    universe = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/universe')
    #: list of terms describing the kind of data
    kind_of_data = xmlmap.StringListField('stdyDscr/stdyInfo/sumDscr/dataKind')
    #: list of notes fields, which may contain other details about the study
    #:
    #: **NOTE:** this and other fields may contain tagged links, which will require
    # some additional work to display as html with clickable links
    study_notes = xmlmap.StringListField('stdyDscr/stdyInfo/notes')

    #: methodology section; list of :class:`Method`
    methods = xmlmap.NodeListField('stdyDscr/method', Method)

    #: data access section, list of :class:`DataAccess`; could be multiple when
    #: conditions differ across files or variables within the collection
    data_access = xmlmap.NodeListField('stdyDscr/dataAccs', DataAccess)

    #: file descriptions, as :class:`FileDescription`; can be repeated if
    #: collection has multiple files
    file_descriptions = xmlmap.NodeListField('fileDscr', FileDescription)

    # technically probably a datefield; could be 4 digit year, or YYYY-MM
    # full xpath is stdyDscr/stdyInfo/sumDscr
    # XPaths for sorting by date  (could be single or date range, doesn't matter)
    # sort on the earliest date available for oldest content
    first_date_xpath = 'min(%(xq_var)s//timePrd/string(@date))'
    # sort on the most recent date for newest content
    last_date_xpath = 'max(%(xq_var)s//timePrd/string(@date))'

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

    # simple DOI regex (does not handle full complexity of DOI spec, but hopefully
    # should work for ICPSR dois )
    doi_re = re.compile('^.*\s(?P<DOI>doi:10\.[0-9]{4,}/\S+)$', flags=re.MULTILINE)

    _doi = None

    @property
    def doi(self):
        if self._doi is None:
            # ICPSR records contain a doi within the citation; if present, extract
            if self.bibligraphic_citation and 'doi:' in self.bibligraphic_citation:
                match = self.doi_re.match(self.bibligraphic_citation)
                if match:
                    self._doi = match.groupdict()['DOI']
        return self._doi

    @property
    def doi_url(self):
        if self.doi:
            return self.doi.replace('doi:', 'http://dx.doi.org/')



    @property
    def geonames_ids(self):
        ''''List of numeric geonames ids from geoCover elements, for
        looking up in the database'''
        return [geo.id[len('geonames:'):] for geo in self.geo_coverage
                        if geo.id is not None]

    @property
    def locations(self):
        ''':class:`~ddisearch.geo.model.Location` objects corresponding
        to the geonames identifiers in the record'''
        return Location.objects.filter(geonames_id__in=self.geonames_ids)

    @property
    def geocoverage_locations(self):
        '''Dictionary of :class:`GeographicCoverage` and matching
        :class:`~ddisearch.geo.models.Location` if available (or None,
        if geogCover element has not been geocoded, or matching db record
        could not be found.'''
        dbloc = self.locations
        # generate a dictionary keyed on geonames id to allow matching up with xml
        dbloc_dict = dict([(l.geonames_id, l) for l in dbloc])
        geog_loc = SortedDict()  # preserve order in the xml
        for geo in self.geo_coverage:
            val = None
            if geo.id is not None:
                val = dbloc_dict.get(int(geo.id[len('geonames:'):]), None)
            geog_loc[geo] = val
        return geog_loc


    @property
    def global_coverage(self):
        return 'Global' in [geo.val for geo in self.geo_coverage]

    @property
    def us_only(self):
        '''Boolean indicating if this dataset only includes regions inside
        the U.S. (For our purposes, records with Puerto Rico coverage will also be
        considered U.S. only).'''
        return self.geonames_ids and \
           self.locations.exclude(country_code__in=['US', 'PR']).count() == 0

    @property
    def us_state_ids(self):
        states = self.locations.order_by('state_code') \
                               .values_list('state_code', flat=True).distinct()
        return list(StateCode.objects.filter(code__in=states).order_by('fips') \
                                .values_list('fips', flat=True).distinct())

    @property
    def country_ids(self):
        '''List of numeric country ids, for highlighting regions covered by the data
        on a topojson map.  If the record explicitly references continents, list of
        ids will include all countries in those continents.'''
        countries = self.locations.order_by('country_code') \
                                  .values_list('country_code', flat=True).distinct()
        # if the record explicitly refers to continents, use that to get all
        # country ids for that continent
        continents = self.locations.filter(feature_code='CONT') \
                                   .order_by('continent_code') \
                                   .values_list('continent_code', flat=True).distinct()
        # find explicitly referenced countries OR countries by continent
        return list(GeonamesCountry.objects.filter(Q(code__in=countries) | Q(continent__in=continents)) \
                                   .order_by('numeric_code') \
                                   .values_list('numeric_code', flat=True).distinct())


# collection prefix normally added by queryset; has to be added explicitly
# here becuase we are including distinct in the primary xpath
_collection = 'collection("/db/%s")' % settings.EXISTDB_ROOT_COLLECTION.lstrip('/')

# template for count xpath: takes collection and xpath (topic or keyword)
# xpath to get the total number of documents with this topic or keyword
# - has to use ft:query or else it is much too slow
_count_xpath_template = '''count(%s/codeBook[ft:query(%s,
        <query><phrase>{%%(xq_var)s}</phrase></query>)])'''
# NOTE: this is not exact... will probably match partials (not great for keywords)
# <regex>^{$n}$</regex> should be possible, but returns count of 0

class DistinctKeywords(XmlModel):
    'xml model to allow searching for distinct keywords'
    objects = Manager('distinct-values(%s//keyword)' % _collection)
    count_xpath = _count_xpath_template % (_collection, './/keyword')
    text = xmlmap.StringField('text()')
    text_xpath = '%(xq_var)s'

class DistinctTopics(XmlModel):
    'xml model to allow searching for distinct local topics'
    objects = Manager('distinct-values(%s//topcClas[@vocab="local"])' % _collection)
    count_xpath = _count_xpath_template % (_collection, './/topcClas[@vocab="local"]')
    text = xmlmap.StringField('text()')
    text_xpath = '%(xq_var)s'



