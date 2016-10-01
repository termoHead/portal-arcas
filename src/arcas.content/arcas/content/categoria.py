# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _

from five import grok
from zope import schema
from plone.app.textfield import RichText
from plone.directives import form
from plone.namedfile.field import NamedBlobImage


from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

COLOR_COLECCION = SimpleVocabulary(
    [SimpleTerm(value=u'7494bf', title=_(u'Celeste')),
     SimpleTerm(value=u'586d57', title=_(u'Verde')),
     SimpleTerm(value=u'c4777b', title=_(u'Rosa')),
     SimpleTerm(value=u'dca167', title=_(u'Naranja')),
     SimpleTerm(value=u'e4d68d', title=_(u'Amarillo')),
     SimpleTerm(value=u'97895e', title=_(u'Marron')),
     SimpleTerm(value=u'd5cfa4', title=_(u'Marron claro')),
     ]
    )


class ICategoria(form.Schema):
    """A conference program. Programs can contain Sessions."""
    color = schema.Choice(
        title=u"Color",
        description=u"El color que identifica esta categoría.",
        vocabulary=COLOR_COLECCION,
    )

    ilustra=NamedBlobImage(
        title=_(u"Imagen"),
        description=_(u"Una imagen que ilustra la categoria en la home"),
        required=False,
    )
