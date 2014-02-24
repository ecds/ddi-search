import os
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from eulexistdb.db import ExistDB, ExistDBException


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
                with open(f, 'r') as xmlfile:
                    success = self.db.load(xmlfile, dbpath, overwrite=True)
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
