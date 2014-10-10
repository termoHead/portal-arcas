# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _

from five import grok
from plone.app.textfield import RichText
from zope import schema
from plone.dexterity.content import Container
from plone.app.textfield import RichText

import z3c.form.field
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobFile
from plone.directives import form

from z3c.relationfield.schema import RelationList, RelationChoice

class IUserFolder(form.Schema):
    """A conference program. Programs can contain Sessions."""
    
    full_cv=NamedBlobFile(
        title=_(u"Curriculum"),
        description=_("Subir un archivo CV"),
        required=False,
    )

 
   

from Acquisition import aq_inner
from plone.directives.dexterity   import DisplayForm
from plone.app.vocabularies.users import UsersSource
from Products.CMFCore.utils import getToolByName
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.utils import ColeccionUtils

class View(DisplayForm):
    grok.context(IUserFolder)
    grok.require('zope2.View')

