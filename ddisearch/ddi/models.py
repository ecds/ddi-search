from eulxml import xmlmap

from eulexistdb.models import XmlModel
from eulexistdb.manager import Manager

class CodeBook(XmlModel):
    # NOTE: may want to adjust xpaths for effeciency when/if we query on them
    title = xmlmap.StringField('stdyDscr/citation/titlStmt/titl')
    abstract = xmlmap.StringField('stdyDscr/stdyInfo/abstract')

    keywords = xmlmap.StringListField('stdyDscr/stdyInfo/subject/keyword')
    topics = xmlmap.StringListField('stdyDscr/stdyInfo/subject/topcClas')

# min($n//timePrd[@event='start' or @event='single']/string(@date))}
    # sort_date = xmlmap.StringField('min(.//timePrd[@event="start" or @event="single"]/string(@date))')
    # sort_date = xmlmap.StringField('.//timePrd/@date')

    # sort = 'min($n//timePrd/string(@date))'

        # sort_date = xmlmap.StringField('.//timePrd[@event="start" or @event="single"]/@date')
    # technically probably a datefield; could be 4 digit year, or YYYY-MM
    # full xpath is stdyDscr/stdyInfo/sumDscr

    dates = xmlmap.NodeListField('.//timePrd', xmlmap.XmlObject)
    start_dates = xmlmap.StringListField('.//timePrd[@event="start"]/@date')
    end_dates = xmlmap.StringListField('.//timePrd[@event="end"]/@date')

    # boosted fields in the index that should be searched to get a tuned
    # relevance score
    boostfields = xmlmap.StringField('.//titl | .//abstract | .//geogCover')

    objects = Manager('/codeBook')


# FIXME: cheating in multiple ways here, figure out a good way to do this....
# need either an 'xquery' field that doesn't get parsed as plain xpath
# or - probably cleaner - a raw sort similar to also/only raw
# (still needs to support ascending/descending logic)
def patch_codebook():
    class PseudoXmlObj(object):
        xpath = None
        def __init__(self, xpath):
            self.xpath = xpath


    print CodeBook._fields
    CodeBook._fields.update({
        'sort_date': PseudoXmlObj('min($n//timePrd/string(@date))')
    })
    print CodeBook._fields

