import logging
import os
from optparse import make_option
import re
import sys
import time
from geopy.geocoders import GeoNames

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from progressbar import ProgressBar, Bar, Percentage, ETA, SimpleProgress

from eulexistdb.db import ExistDB, ExistDBException
from eulxml.xmlmap import load_xmlobject_from_file

from ddisearch.ddi.models import CodeBook, Topic
from ddisearch.ddi.topics import topic_mappings, conditional_topics
from ddisearch.geo.models import Location, GeonamesCountry, GeonamesContinent

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    args = '<filename filename filename ...>'
    help = '''Loads XML files into the configured eXist collection.
    The local copy will be *removed* after it is successfully loaded.'''

    option_list = BaseCommand.option_list + (
        make_option('--dry-run', '-n',
            dest='dryrun',
            action='store_true',
            help='''Report on what would be done, but don't delete any files'''
        ),
    )

    v_normal = 1
    def handle(self, *files, **options):
        verbosity = int(options.get('verbosity', self.v_normal))

        # check for required settings
        if not hasattr(settings, 'EXISTDB_ROOT_COLLECTION') or \
           not settings.EXISTDB_ROOT_COLLECTION:
            raise CommandError("EXISTDB_ROOT_COLLECTION setting is missing")
            return

        self.db = ExistDB()
        self.geonames = GeoNames(username=settings.GEONAMES_USERNAME)

        # initalize progress bar
        pbar = None
        total = len(files)
        # init progress bar if processing enough files, running on a terminal
        if total >= 10 and os.isatty(sys.stderr.fileno()):
            widgets = [Percentage(), ' (', SimpleProgress(), ')',
                       Bar(), ETA()]
            pbar = ProgressBar(widgets = widgets, maxval=total).start()

        errored = 0
        loaded = 0
        for f in files:
            success = False

            if pbar:
                pbar.update(errored + loaded)

            try:
                # full path location where file will be loaded in exist db collection
                dbpath = settings.EXISTDB_ROOT_COLLECTION + "/" + os.path.basename(f)
                # TODO: any error checking? validation?

                start = time.time()
                cb = load_xmlobject_from_file(f, CodeBook)
                logger.debug('%s loaded as xml in %f sec' % (f, time.time() - start))

                start = time.time()
                self.prep(cb)
                logger.debug('%s prepped in %f sec' % (f, time.time() - start))
                # load to eXist from string since DDI documents aren't that large,
                # rather than reloading the file
                if not options['dryrun']:
                    start = time.time()
                    success = self.db.load(cb.serialize(pretty=True), dbpath, overwrite=True)
                    logger.debug('%s loaded to eXist in %f sec' % (f, time.time() - start))

            except IOError as e:
                self.stdout.write("Error opening %s: %s" % (f, e))
                errored += 1

            except ExistDBException as e:
                self.stdout.write("Error: failed to load %s to eXist" % f)
                self.stdout.write(e.message())
                errored += 1

            if not options.get('dryrun', False) and success:
                loaded += 1
                if verbosity > self.v_normal:
                    self.stdout.write("Loaded %s as %s" % (f, dbpath))

                try:
                    os.remove(f)
                except OSError as e:
                    self.stdout.write('Error removing %s: %s' % (f, e))

        if pbar:
           pbar.finish()

        # output a summary of what was done if more than one file was processed
        if verbosity >= self.v_normal:
            if loaded > 1:
                self.stdout.write("%d document%s loaded" % \
                                  (loaded, 's' if loaded != 1 else ''))
            if errored > 1:
                self.stdout.write("%d document%s with errors" % \
                                  (errored, 's' if errored != 1 else ''))

    topic_id = re.compile('^(?P<org>[A-Z]+)[ .](?P<id>[IVX]+(\.[A-Z](\.[0-9]+(\.[a-z]+)?)?)?)')


    def prep(self, cb):
        # do any prep work or cleanup that needs to be done
        # before loading to exist
        self.local_topics(cb)
        self.clean_dates(cb)
        self.geography(cb)

    def icpsr_topic_id(self, topic):
        # generate icpsr topic id in the format needed for lookup in our
        # topic dictionary; returns None if not an ICPSR topic
        m = self.topic_id.match(topic)
        if m:
            match_info = m.groupdict()
            if match_info['org'] == 'ICPSR':
                return '%(org)s.%(id)s' % match_info

    def local_topics(self, cb):
        # convert ICPSR topics to local topics
        for t in cb.topics:
            topic_id = self.icpsr_topic_id(t.val)
            if topic_id is not None:
                new_topic = topic_mappings.get(topic_id, None)
                if new_topic:
                    cb.topics.append(Topic(val=new_topic,
                        vocab='local'))

                # conditional topics if the geographic coverage is global
                if topic_id in conditional_topics['global'] and \
                  'Global' in [unicode(gc) for gc in cb.geo_coverage]:
                    cb.topics.append(Topic(val=conditional_topics['global'][topic_id],
                                           vocab='local'))

    def clean_dates(self, cb):
        # clean up dates so we can search consistently on 4-digit years
        # or more; dates should be YYYY, YYYY-MM, or YYYY-MM-DD
        prev_date = None
        for d in cb.time_periods:
            # special case: two-digit date as second date in a cycle
            # interpret as month on the year that starts the cycle
            if d.event == 'end' and d.cycle == prev_date.cycle and \
                    len(d.date) == 2:
               d.date = '%04d-%02d' % (int(prev_date.date), int(d.date))

            elif len(d.date) < 4:
                d.date = '%04d' % int(d.date)

            # store current date as previous date for next loop, in case
            # we need to clean up an end date in a cycle
            prev_date = d

    def geography(self, cb):
        if cb.geo_unit:
            logger.debug('geog unit = %s' % '; '.join(cb.geo_unit))
        for geog in cb.geo_coverage:
            logger.info(geog.val)
            if geog.val == 'Global':
                # do we anything here?
                continue

            # first check in the db, in case we've looked up before
            db_locations = Location.objects.filter(name=geog.val)
            # FIXME: logic to handle Georgia here
            if db_locations.count():
                # store db location so we can put geonames id into the xml
                dbloc = db_locations[0]

            else:
                loc = self.geonames.geocode(geog.val)
                if not loc:
                    print 'no match found for %s' % geog.val
                    continue
                logger.debug(unicode(loc))
                logger.debug(loc.raw)

                # TODO: extra logic for interpreting Georgia as state/country?
                # if locations include US and any US states, should be state
                # if locations include US and other countries, should be country
                # FIXME: for some reason 'Europe' is geocoded as 'Minsk' and
                # 'Africa' is geocoded as 'Camayenne'

                # check if geonames id is already in the db
                db_locations = Location.objects.filter(geonames_id=loc.raw['geonameId'])
                if db_locations.count():
                    dbloc = db_locations[0]
                else:
                    # if not, create new db location from geonames lookup

                    # determine continent code based on country
                    country_code = loc.raw.get('countryCode', None)
                    continent_code = None
                    if country_code is not None:
                        try:
                            c = GeonamesCountry.objects.get(code=country_code)
                            continent_code = c.continent
                        except:
                            pass

                    # special case for continents
                    elif loc.raw['fcode'] == 'CONT':
                        try:
                            c = GeonamesContinent.objects.get(geonames_id=loc.raw['geonameId'])
                            continent_code = c.code
                        except:
                            pass

                    state_code = None
                    admin_code = loc.raw.get('adminCode1', None)
                    if admin_code and admin_code != '00':
                        state_code = admin_code

                    dbloc = Location(name=loc.raw['name'],
                        geonames_id=loc.raw['geonameId'],
                        latitude=loc.latitude,
                        longitude=loc.longitude,
                        country_code=country_code,
                        feature_code=loc.raw['fcode'],
                        continent_code=continent_code,
                        state_code=state_code)
                    # possibly fcode is useful here - "feature code",
                    # see http://www.geonames.org/export/codes.html
                    # CONT = continent
                    dbloc.save()

                    # TODO: make sure hierarchy is present?
                    # - continent, country, state (?)

            # set geonames id in the xml
            geog.id = 'geonames:%d' % dbloc.geonames_id
            logger.info('setting geonames id to %s' % geog.id)





