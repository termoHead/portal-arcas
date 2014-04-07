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
from plone.namedfile.field import NamedBlobImage
from plone.directives import form

from z3c.relationfield.schema import RelationList, RelationChoice

class IColeccion(form.Schema):
    """A conference program. Programs can contain Sessions."""
    form.fieldset(
        'responsables',
        u"Responsables",
        fields=['coordinador','integrantes'],
    )
    form.fieldset(
        'imagenes',
        u"Ilustraciones",
        fields=['imagenCabecera','imagenHome','imagenLista'],
    )

    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=False,
    )

    coordinador=schema.List(
        title=_("Coordinador"),
        value_type=schema.Choice(source="arcas.CoorMembersVocab",),
        required=False,
    )
    integrantes=schema.List(
        title=_("Integrantes"),
        value_type=schema.Choice(source="arcas.InvestMembersVocab",),
        required=False,
    )
    imagenCabecera=NamedBlobImage(
        title=_(u"Imagen de la cabecera de la coleccion"),
        description=_("Esta imagen se usa como cabezal en la visualizacion de la coleccion"),
        required=False,
    )
    imagenHome=NamedBlobImage(
        title=_(u"Imagen para mostrar en la pagina principal"),
        description=_("Esta imagen se usa en la home"),
        required=False,
    )

    imagenLista=NamedBlobImage(
        title=_(u"Imagen para listado"),
        description=_("Esta imagen se usa en el listado de colecciones"),
        required=False,
    )

    GS_ID= schema.TextLine(
        title=u"ID de la coleccion",
        description=u"Nombre de la coleccion en GS3. Se requiere para hacer las busquedas",
        required=True,
    )
    creativeURL=schema.TextLine(
        title=_(u"URL al Creative Commons"),
        required=False,
    )

from Acquisition import aq_inner
from plone.directives.dexterity   import DisplayForm
from plone.app.vocabularies.users import UsersSource
from Products.CMFCore.utils import getToolByName
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.utils import ColeccionUtils

class View(DisplayForm):
    grok.context(IColeccion)
    grok.require('zope2.View')

    def getCoordinadores(self):
        """Devuelve los curadores de la coleción"""
        colec=ColeccionUtils(self.context)
        infoCoor=colec.getCoordinadores()
        return infoCoor

    def getUrlAFuente(self):
        """devuelv la dirección a la fuente primaria"""
        baseURL=URL_GREENSTON_DOC+self.context.GS_ID+"/browse/CL1"
        return baseURL
    def dameCurador(self):
        """devuelve un listado con los curadores de la coleccion"""
        rs=ColeccionUtils(self.context)
        rt=rs.dameCurador()
        return rt

    def dameDicRecomendados(self):
        """
            devuelve un listado de las carpetas y sus contenidos como recomendados
        """
        idRec=self.context.id+"_recom"
        listFold=[]
        if hasattr(self.context,idRec):
            recomFolder=aq_inner(self.context[idRec])
            objRaiz={}
            objRaiz["titulo"]="Recomendaciones"
            objRaiz["content"]=self.dameContenido(recomFolder)
            objRaiz["url"]=self.context.absolute_url
            listFold.append(objRaiz)
            for elem in recomFolder.getFolderContents():
                elemObj=self.context.unrestrictedTraverse(elem.getPath())

                if elem.portal_type=="Folder":
                    obj={}
                    obj["titulo"]   =elem.Title
                    obj["content"]  =self.dameContenido(elemObj)
                    obj["url"]  =elem.getURL()
                    listFold.append(obj)
            return listFold
        else:
            print "la coleccion no tiene carpeta Recomendados"
            return None



    def dameContenido(self,folder):
        """Devuelve una lista con los objetos del contenedor"""
        resultado=[]

        for elem in folder.getFolderContents():
            if elem.portal_type!="Folder":
                elemObj = folder.unrestrictedTraverse(elem.getPath())

                urlE    = elem.getURL()

                if elem.portal_type=="Link" or elem.portal_type=="arcas.sugerencia":
                    if hasattr(elemObj,"getRemoteUrl") and elemObj.getRemoteUrl!='':
                        urlE=getRemoteUrl.getRemoteUrl


                tipoMedio=False
                listAutores=[]
                if hasattr(elemObj,"tipoMedio"):
                    tipoMedio=getattr(elemObj,"tipoMedio")
                    if tipoMedio=='resena':
                        tipoMedio='reseña'

                if hasattr(elemObj,"autores"):
                    listAutores=getattr(elemObj,"autores")

                objRaiz={'titulo':elem.Title,
                         'url':urlE,
                         'descri':elem.Description,
                         'tipo':tipoMedio,
                         'autores':listAutores,
                         }

                resultado.append(objRaiz)

        return resultado


    def getImagenes(self):
        """Devuelve todas las img de la galeria"""
        context = aq_inner(self.context)
        catalogo=getToolByName(context,"portal_catalog")
        tmpX=[]
        if hasattr(context,context.id+"_gale"):
            galeFold=context[context.id+"_gale"]
            galePath="/".join(galeFold.getPhysicalPath())
            result=catalogo(path=galePath,portal_type="Image")
            
            for re in result:
                foto=context.unrestrictedTraverse(re.getPath())
                iniH=foto.height
                altoSugerido=80
                relH=((altoSugerido*100)/iniH)
                widthH=(foto.width*relH)/100
                tmpX.append({"width":widthH,"brain":re})

        else:
            return None

        return tmpX
        

    def getBioList(self):
        """Devuelve un listado de biografías que ese encuentra dentro de de la colección"""
        listBio=[]
        contexto=self.context.aq_inner
        for bio in contexto.getFolderContents():
            if bio.portal_type=="arcas.biografia":
                listObj=contexto.unrestrictedTraverse(bio.getPath())
                listBio.append({
                    "nombre":bio.Title,
                    "descri":bio.Description,
                    "url":bio.getURL(),
                    "listado":listObj.produccion.output,
                })

        return  listBio

    def dameBanners(self):
        """Devuleve los banners a las exhibiciones relacionadas a la coleccion"""
        utilidad= ColeccionUtils(self.context)
        result=[]
        for exhi in utilidad.dameExhibicionesR():
            obj={'url':exhi.absolute_url(),'titulo':exhi.title}
            result.append(obj)
        return  result
