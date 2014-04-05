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


class ICurador(form.Schema):
    """Biografía de un personaje
    """
    title = schema.TextLine(title=u"Nombre",description=u"Nombre y apellido del curador")
    bio = RichText(
        title=_(u"Texto principal"),
        required=True,
    )
    retrato=NamedBlobImage(
        title=u"Foto del curador",
        description=u"Imagen a modo de retrato. Tamaño 79*79px",
        required=False,
    )



from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm
from arcas.content.behaviors import IColecGroupName



class View(DisplayForm):
    grok.context(ICurador)
    grok.require('zope2.View')