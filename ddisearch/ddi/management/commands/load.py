import os
import re
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from eulexistdb.db import ExistDB, ExistDBException
from eulxml.xmlmap import load_xmlobject_from_file

from ddisearch.ddi.models import CodeBook, Topic
from ddisearch.ddi.topics import topic_mappings, conditional_topics


class Command(BaseCommand):
    args = '<filename filename filename ...>'
    help = '''Loads XML files into the configured eXist collection.
    The local copy will be *removed* after it is successfully loaded.'''

    v_normal = 1
    def handle(self, *files, **options):
        verbosity = int(options.get('verbosity', self.v_normal))

        # check for required settings
        if not hasattr(settings, 'EXISTDB_ROOT_COLLECTION') or \
           not settings.EXISTDB_ROOT_COLLECTION:
            raise CommandError("EXISTDB_ROOT_COLLECTION setting is missing")
            return

        self.db = ExistDB()

        errored = 0
        loaded = 0
        for f in files:
            success = False
            try:
                # full path location where file will be loaded in exist db collection
                dbpath = settings.EXISTDB_ROOT_COLLECTION + "/" + os.path.basename(f)
                # TODO: any error checking? validation?

                cb = load_xmlobject_from_file(f, CodeBook)
                self.prep(cb)
                # load to eXist from string since DDI documents aren't that large,
                # rather than reloading the file
                success = self.db.load(cb.serialize(pretty=True), dbpath, overwrite=True)

            except IOError as e:
                self.stdout.write("Error opening %s: %s" % (f, e))
                errored += 1

            except ExistDBException as e:
                self.stdout.write("Error: failed to load %s to eXist" % f)
                self.stdout.write(e.message())
                errored += 1

            if success:
                loaded += 1
                if verbosity > self.v_normal:
                    self.stdout.write("Loaded %s as %s" % (f, dbpath))

                try:
                    os.remove(f)
                except OSError as e:
                    self.stdout.write('Error removing %s: %s' % (f, e))

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
                  'Global' in cb.geo_coverage:
                    cb.topics.append(Topic(val=conditional_topics['global'][topic_id],
                                           vocab='local'))



