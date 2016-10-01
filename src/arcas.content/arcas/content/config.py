# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _
#La constantea es la base para un documento de greenstone
#luego viene la colección elegida puig y la cadena fija "/document"
#URL_GREENSTON_DOC="http://g3:8383/greenstone3/library/collection/"
URL_GREENSTON_DOC="http://arcas.fahce.unlp.edu.ar:8383/greenstone3/library/collection/"



from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
TIPOS_COLECCION = SimpleVocabulary(
    [SimpleTerm(value=u'0', title=_(u'Autor')),
     SimpleTerm(value=u'1', title=_(u'Corpus Linguisticos'))
     ]
    )

