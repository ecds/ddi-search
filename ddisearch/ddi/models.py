from eulxml import xmlmap

from eulexistdb.models import XmlModel
from eulexistdb.manager import Manager

class CodeBook(XmlModel):
    # NOTE: may want to adjust xpaths for effeciency when/if we query on them
    title = xmlmap.StringField('stdyDscr/citation/titlStmt/titl')
    abstract = xmlmap.StringField('stdyDscr/stdyInfo/abstract')

    keywords = xmlmap.StringListField('stdyDscr/stdyInfo/subject/keyword')
    topics = xmlmap.StringListField('stdyDscr/stdyInfo/subject/topcClas')

    objects = Manager('/codeBook')

