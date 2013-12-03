from eulxml import xmlmap

from eulexistdb.models import XmlModel
from eulexistdb.manager import Manager

class CodeBook(XmlModel):
    title = xmlmap.StringField('docDscr/citation/titlStmt/titl')

    objects = Manager('/codeBook')

