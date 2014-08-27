'''
Django website for search and display access to DDI XML descriptions
of research datasets such as those provided by the ICPSR.  Uses
eXist-db for powerful full text searching.

'''

__version_info__ = (1, 0, 0, 'dev')

# Dot-connect all but the last. Last is dash-connected if not None.
__version__ = '.'.join(str(i) for i in __version_info__[:-1])
if __version_info__[-1] is not None:
    __version__ += ('-%s' % (__version_info__[-1],))
