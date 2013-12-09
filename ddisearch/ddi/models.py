from eulxml import xmlmap

from eulexistdb.models import XmlModel
from eulexistdb.manager import Manager

class CodeBook(XmlModel):
    # NOTE: may want to adjust xpaths for effeciency when/if we query on them
    title = xmlmap.StringField('stdyDscr/citation/titlStmt/titl')
    abstract = xmlmap.StringField('stdyDscr/stdyInfo/abstract')
    authors = xmlmap.StringListField('stdyDscr/citation/rspStmt/AuthEnty')

    keywords = xmlmap.StringListField('stdyDscr/stdyInfo/subject/keyword')
    topics = xmlmap.StringListField('stdyDscr/stdyInfo/subject/topcClas')

    dates = xmlmap.NodeListField('.//timePrd', xmlmap.XmlObject)
    # technically probably a datefield; could be 4 digit year, or YYYY-MM
    # full xpath is stdyDscr/stdyInfo/sumDscr
    sort_date_xpath = 'min(%(xq_var)s//timePrd/string(@date))'

    # boosted fields in the index that should be searched to get a tuned
    # relevance score
    boostfields = xmlmap.StringField('.//titl | .//abstract | .//geogCover')

    objects = Manager('/codeBook')


