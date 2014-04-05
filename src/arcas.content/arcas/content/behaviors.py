# -*- coding: utf-8 -*-
__author__ = 'Paul'
"""Behaviours to assign tags (to ideas).

Includes a form field and a behaviour adapter that stores the data in the
standard Subject field.
"""

from rwproperty import getproperty, setproperty

from zope.interface import implements, alsoProvides
from zope.component import adapts
from zope import schema
from plone.directives import form
from Products.CMFCore.interfaces import IDublinCore
from arcas.content import ArcasMessageFactory as _
from arcas.content.coleccion import IColeccion
from Acquisition import aq_inner, aq_base

ID_SET=""
class IColecGroupName(form.Schema):
    """Add tags to content
    """
    form.fieldset(
        'responsables',
        u"Responsables",
        fields=['groupName'],
    )
    groupName= schema.TextLine(
        title=_(u"Nombre del grupo"),
        description=_(u"La coleccion tiene asociado un grupo de usuarios, este campo define el nombre de dicho grupo"),
        required=False,
        default=u"sinNombre"
    )


@form.default_value(field = IColecGroupName['groupName'],context=IColeccion)
def excludeFromNavDefaultValue(data):
    return data.groupName

alsoProvides(IColecGroupName, form.IFormFieldProvider)

class ColecGroupName(object):
    """Store tags in the Dublin Core metadata Subject field. This makes
        tags easy to search for."""
    implements(IColecGroupName)
    adapts(IColeccion)


    def __init__(self, context):
        self.seteado=0
        self.context = context


    @getproperty
    def groupName(self):

            try:
                return self.context.aq_base.id+"_g"
            except :
                return "sinNombre"


    @setproperty
    def groupName(self, value):
        if value is None:
            value = ()
        self.contevaluext.aq_base.setGroupName()

