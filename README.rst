README
======

.. image:: https://img.shields.io/github/license/emory-libraries/ddi-search.svg
  :alt: License

.. image:: https://travis-ci.org/emory-libraries/ddi-search.svg?branch=feature/django-upgrade
  :target: https://travis-ci.org/emory-libraries/ddi-search
  :alt: travis-ci build

.. image:: https://coveralls.io/repos/github/emory-libraries/ddi-search/badge.svg?branch=feature/django-upgrade
  :target: https://coveralls.io/github/emory-libraries/ddi-search?branch=feature/django-upgrade
  :alt: Code Coverage

.. image:: https://codeclimate.com/github/emory-libraries/ddi-search/badges/gpa.svg
  :target: https://codeclimate.com/github/emory-libraries/ddi-search
  :alt: Code Climate

.. image:: https://requires.io/github/emory-libraries/ddi-search/requirements.svg?branch=feature/django-upgrade
  :target: https://requires.io/github/emory-libraries/ddi-search/requirements/?branch=feature/django-upgrade
  :alt: Requirements Status

DDI Search
^^^^^^^^^^

Django website for search and display of research dataset descriptions
marked up using
`Data Documentation Initiative (DDI) XML <http://www.ddialliance.org/>`_ version 2.1.

The site provides access to records via browse by topic, browse by
geography (using custom geocoding logic and the `GeoNames.org
<geonames.org>`_ API), and search by simple keyword with an optional
advanced search providing access to search by specific fields and/or
filter by year.   Search results are returned in a card-based layout
with an optional preview.  The full record view provides details in a
readable format, displaying a DOI extracted from the record citation
(when available), and links to provide access to the original record (in
the case of ICPSR materials) and instructions to access the data. Full
record view includes a U.S. or world map providing a visual indicator of
the geographical coverage, based on the same custom geocoding.

XML search and display is provided by `eXist-DB <http://exist-db.org/>`_
using `eulexistdb <https://github.com/emory-libraries/eulexistdb>`_.

-----

For more detailed information, including installation instructions and upgrade
notes, see :ref:`DEPLOYNOTES`.  For details about the features included in each release,
see :ref:`CHANGELOG`.
