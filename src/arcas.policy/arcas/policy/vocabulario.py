# -*- coding: utf-8 -*-
__author__ = 'Paul'

from zope.interface import implements
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from arcas.content.coleccion import IColeccion
from zope.site.hooks import getSite

class ListaColecciones(object):
    """
    Devuelve un listado con las colecciones activas
    """
    implements(IVocabularyFactory)
    def __init__(self):
        pass

    def __call__(self, context):
        contexto=getSite()
        catalogo= getToolByName(contexto, 'portal_catalog')
        results=catalogo.unrestrictedSearchResults({'object_provides': IColeccion.__identifier__,'review_state':('SetUp','Publicado')})
        terms = []
    
        if len(results)>0:
            for colec in results:

                terms.append(SimpleVocabulary.createTerm(colec.id, str(colec.id), colec.Title))
        return SimpleVocabulary(terms)


ColeccionesVocabFactory = ListaColecciones()
