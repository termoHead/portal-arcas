# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _

from five import grok
from plone.app.textfield import RichText
from zope import schema
from plone.dexterity.content import Container
from plone.dexterity.browser import add
from plone.app.textfield import RichText
from Products.CMFCore.utils import getToolByName
import z3c.form.field
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from plone.directives import form, dexterity
from Products.validation.interfaces.IValidator import IValidator
from Products.validation import validation
from z3c.form import validator
from zope.interface import Invalid
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.indexer import indexer




def isValidURL(value):
    if value.find("http://")==0:
        return True
    else:
        raise Invalid(_(u"Por favor ingrese un una url que incluya HTTP"))


    
tiposVocab = SimpleVocabulary(
    [SimpleTerm(value=u'imagen', title='Imagen'),
     SimpleTerm(value=u'audio', title='Audio'),
     SimpleTerm(value=u'video', title='Video'),
     SimpleTerm(value=u'texto', title='Texto'),
     SimpleTerm(value=u'web', title='Página web')]
)
tipoEnlaceVocab = SimpleVocabulary(
    [
        SimpleTerm(value=0, title='A Greenstone'),
        SimpleTerm(value=1, title='Independiente'),
     ]
)

class IEnlacegs(form.Schema):
    """A conference program. Programs can contain Sessions.
    """
    
    
    cuerpo = RichText(
        title=u"Enlace a la fuente primaria",
        required=True,
    ) 
    
    tipoMedio = schema.Choice(
        title=_(u"Tipo de recurso"),
        vocabulary=tiposVocab,
        required=True,
    )
    form.widget('tipoEnlace', 
    onchange=u"ocultaCamposEnlaceGS($(this).val())")
    tipoEnlace = schema.Choice(
        title=_(u"Tipo de enlace"),
        description=u"Especifique si el recurso que quiere publicar está en el Repositorio de Arcas, o si es independiente.",
        vocabulary=tipoEnlaceVocab,
        required=True,
    )
    
   
    ficha = schema.TextLine(
        title=_(u"Enlace al documento"),
        description=u"Enlace al documento Greenstone (debe incluir el http://)",
        required=False,
        constraint=isValidURL,        
    )
    urlRemoto= schema.TextLine(
        title=u"Enlace a la fuente primaria",
        description=u"Enlace a la fuente primaria en Greenstone, debe incluir el http://",
        required=False,
        constraint=isValidURL,
    )
    

    
@grok.adapter(IEnlacegs, name='urlRemoto')
@indexer(IEnlacegs)
def remoteURLIndexer(context):
    return context.urlRemoto

from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm
from arcas.content.behaviors import IColecGroupName
from z3c.form import interfaces

class View(DisplayForm):
    grok.context(IEnlacegs)
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

    def dameSeccion(self):
        padre=self.context.aq_parent
        return padre.title

    def dameImagen(self):
        return self.context.urlRemoto

    def dameThumb(self):
        remplazo=self.context.urlRemoto.replace("screen.jpeg","thumb.gif")
        return remplazo

from arcas.theme.interfaces import IArcasTheme


class AddForm(dexterity.AddForm):
    #portal_type = 'arcas.enlacegs'
    grok.layer(IArcasTheme)
    grok.name('arcas.enlacegs')
    grok.context(IEnlacegs)
    
    
        
    def update(self):       
        super(AddForm, self).update()
        
        
                  
        """f fTipo.value[0]=="1":
            print "Uno"
            #self.widgets["ficha"].value=""
            #self.widgets["urlRemoto"].value=""
            fFicha.mode=interfaces.DISPLAY_MODE
            fUrl.mode=interfaces.DISPLAY_MODE
        else:
            print "Dos"       
            fFicha.mode=interfaces.HIDDEN_MODE
            fUrl.mode=interfaces.HIDDEN_MODE
        """        
        pass
        
            
    def updateActions(self):
        super(AddForm, self).updateActions()
        pass
        """
        fTipo=self.widgets["tipoEnlace"]
        fFicha=self.widgets["ficha"]
        fUrl=self.widgets["urlRemoto"]
        
        if len(fTipo.value)>0:
            if fTipo.value[0]=="1":
                print "Uno"           
                fFicha.mode=interfaces.DISPLAY_MODE
                fUrl.mode=interfaces.DISPLAY_MODE
            else:
                print "Dos"       
                fFicha.mode=interfaces.HIDDEN_MODE
                fUrl.mode=interfaces.HIDDEN_MODE
            
        fFicha.update()
        fUrl.update()
        """