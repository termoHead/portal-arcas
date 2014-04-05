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
from plone.z3cform.textlines.textlines import TextLinesFieldWidget
tiposVocab = SimpleVocabulary(
    [SimpleTerm(value=u'articulo', title='Artículo'),
     SimpleTerm(value=u'audio', title='Audio'),
     SimpleTerm(value=u'resena', title='Reseña'),
     SimpleTerm(value=u'texto', title='Texto'),
     SimpleTerm(value=u'video', title='Video'),
     SimpleTerm(value=u'web', title='Página web')]
)


def isValidURL(value):
    if value.find("http://")==0:
        return True
    else:
        raise Invalid(_(u"Por favor ingrese un una url que incluya HTTP"))

class ISugerencia(form.Schema):
    """
    Sugerencia de lectura que complementa una colección o una exhibición
    """
    tipoMedio = schema.Choice(
        title=u"Tipo de sugerencia",
        vocabulary=tiposVocab,
        required=True,
    )


    form.widget(autores=TextLinesFieldWidget)
    autores = schema.List(
        title=u"Autores o responsables",
        description=u"Cargar un autor por linea",
        required=False,
        default=[],
        value_type=schema.TextLine(),
    )

    urlRemoto= schema.TextLine(
        title=u"Enlace externo",
        description=u"Enlace. debe incluir el http://",
        required=False,
        constraint=isValidURL,
    )

@grok.adapter(ISugerencia, name='urlRemoto')
@indexer(ISugerencia)
def remoteURLIndexer(context):
    return context.urlRemoto



@grok.adapter(ISugerencia, name='urlRemoto')
@indexer(ISugerencia)
def remoteURLIndexer(context):
    return context.urlRemoto

from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm
from arcas.content.behaviors import IColecGroupName


class View(DisplayForm):
    grok.context(ISugerencia)
    grok.require('zope2.View')

    def dameIcon(self):
        """Devuelve un icono segun el tipo elegido"""
        if self.context.tipoMedio==u"imagen":
            return "imagen_icon.gif"
        elif self.context.tipoMedio==u"audio":
            return "audio_icon.gif"
        elif self.context.tipoMedio==u"texto":
            return "text_icon.gif"
        elif self.context.tipoMedio==u"video":
            return "video_icon.gif"
        elif self.context.tipoMedio==u"web":
            return "web_icon.gif"
        elif self.context.tipoMedio==u"resena":
            return "resena_icon.gif"
        elif self.context.tipoMedio==u"articulo":
            return "articulo_icon.gif"