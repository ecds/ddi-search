.. _DEPLOYNOTES:

DEPLOYNOTES
===========

Installation
------------

Instructions to install required software and systems, configure the application,
and run various scripts to load initial data.

Software Dependencies
~~~~~~~~~~~~~~~~~~~~~

We recommend the use of `pip <http://pip.openplans.org/>`_ and `virtualenv
<http://virtualenv.openplans.org/>`_ for environment and dependency
management in this and other Python projects. If you don't have them
installed, you can get them with ``sudo easy_install pip`` and then
``sudo pip install virtualenv``.

------

Bootstrapping a development environment
---------------------------------------

* Copy ``ddisearch/localsettings.py.dist`` to ``ddisearch/localsettings.py``
  and configure your local settings:
  - **DATABASES** - sql database, used for browse by geography
  - **EXIST_** database configuration, server url and collection where DDI
    xml data will be loaded
  - Django **SECRET_KEY**
  - **LOGGING** (if using file logger, ensure path exists and is writable)
  - **GEONAMES_USERNAME** - `GeoNames.org webservice account <http://www.geonames.org/export/web-services.html>`_,
    for use in geocoding locations when loading data
* Create a new virtualenv and activate it.
* Install fabric: ``pip install fabric``
* Use fabric to run a local build, which will install python dependencies in
  your virtualenv, run unit tests, and build sphinx documentation: ``fab build``


Deploy to QA and Production should be done using ``fab deploy``.


After the **EXIST_** settings for accessing an eXist-db collection have
been configured in the local settings, load the index via::

    python manage.py existdb load-index -u dbauser -p

If data was loaded before the index conifguration was loaded, you should
reindex the data::

    python manage.py existdb reindex -u dbauser -p

.. Note::

  Because this site is configured to access the content in the eXist
  database anonymously, credentials for an eXist account with dba access
  must be passed to the existdb script when managing the index configuration
  or reindexing content.

ICPSR and any local DDI XML files should be loaded to the appropriate eXist
collection using the Java client, WebDAV, or similar.  For testing purposes,
you can load a `sample CodeBook <http://www.icpsr.umich.edu/icpsrweb/ICPSR/ddi2/studies/4245>`_
provided as a `markup example <http://www.ddialliance.org/resources/markup-examples>`_,
or you may load the fixture included for unit tests in `ddisearch.ddi.fixtures`.

If you want your DDI documents geocoded for display in the geographical browse,
use the load command ``python manage.py load``; this requires a
valid **GEONAMES_USERNAME** configured in localsettings.  You may also
need to configure credentials for an **EXISTDB_SERVER_USER**
and **EXISTDB_SERVER_PASSWORD** with access to add files to your configured
collection.  Also, be aware that the script is designed to remove the local
copy of any files that are successfully loaded.


