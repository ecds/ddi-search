README
======

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
