# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _

from five import grok
from plone.app.textfield import RichText
from zope import schema
from plone.dexterity.content import Container
from plone.app.textfield import RichText
from Products.CMFCore.utils import getToolByName
import z3c.form.field
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from plone.directives import form
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from z3c.form import validator
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.indexer import indexer

class IBiografia(form.Schema):
    """Biografía de un personaje
    """

    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=True,
    )
    produccion = RichText(
        title=_(u"Obras o datos relevante"),
        description=_(u"Listar las obras/acciones/hitos más relevantes del artista"),
        required=True,
    )


from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm
from arcas.content.behaviors import IColecGroupName

from Acquisition import aq_parent

class View(DisplayForm):
    grok.context(IBiografia)
    grok.require('zope2.View')

    def dameColeccionNombre(self):
        padre=aq_parent(self.context)

        return padre.Title()