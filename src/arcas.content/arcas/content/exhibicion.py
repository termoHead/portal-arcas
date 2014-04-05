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
from arcas.content.behaviors import IColecGroupName
from arcas.content.eventos import PREFIJO_COOR_GROUP
from arcas.content.coleccion import IColeccion

from z3c.relationfield.schema import RelationList, RelationChoice
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.formwidget.autocomplete import AutocompleteFieldWidget
from plone.formwidget.contenttree import ContentTreeFieldWidget
class IExhibicion(form.Schema):
    """A conference program. Programs can contain Sessions.
    """
    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=False,
    )
    bgCabezalHome=NamedBlobImage(
        title=_(u"Imagen Home"),
        description=u"Imagen de fondo que se utiliza en la home. Para componerla utilice los ejemplos del banco de imagenes",
        required=False,
    )
    bgCabezalVista=NamedBlobImage(
        title=_(u"Imagen de la vista"),
        description=u"Imagen de fondo que se utiliza en la pagina de la exhibición propiamente dicha. Si desea componer una nueva, utilice los ejemplos del banco de imagenes",
        required=False,
    )
    bgCabezalLista=NamedBlobImage(
        title=_(u"Imagen para el listado exhibiciones"),
        description=u"Imagen de fondo que se utiliza en el listado de exhibiciones. Si desea componer una nueva, utilice los ejemplos del banco de imagenes",
        required=False,
    )
    baner=NamedBlobImage(
        title=_(u"Imagen para baner"),
        description=u"Imagen completa del baner que se muestra en la vista de coleccion. Si desea componer uno nuevo, puede utilizar los ejemplos del banco de imágenes",
        required=False,
    )
    form.widget('coleccionR', ContentTreeFieldWidget)
    coleccionR = RelationChoice(
        title=u"Coleccion a la que corresponde",
        description=u"Seleccione la Coleccion a la que pertenece esta exhibicion",
        source=ObjPathSourceBinder(object_provides=IColeccion.__identifier__),
        required=False,
    )

from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm

class View(DisplayForm):
    grok.context(IExhibicion)
    grok.require('zope2.View')

    def listadoDeImagenesGS3(self):
        """Trae todos los recursoGS3 en la carpeta enlacesgs"""
        catalog=getToolByName(self.context,"portal_catalog")
        ruta='/'.join(self.context.getPhysicalPath())
        result=catalog(portal_type='arcas.enlacegs', review_state='published',path={'query': ruta, 'depth': 1})

        return result

    def muestraImagenGS(self):
        """Tra una imagen de GS3"""
        pass

    def dameObjectoColeccion(self):
        from arcas.content.coleccion import IColeccion
        try:
            miColec=self.context.coleccionR.to_object

            if IColeccion.providedBy(miColec):
                return miColec
            else:
                return None
        except:
            print "no hay coleccion asignada"
        return None


    def dameCoords(self):
        """Devuelve los usuarios del grupo coor"""
        groups_tool = getToolByName(self.context, 'portal_groups')
        fUser=[]

        colecR=self.dameObjectoColeccion()

        if colecR:
            ppa=IColecGroupName(colecR)
            group_id = ppa.groupName.replace("_g",PREFIJO_COOR_GROUP)
            grupo=groups_tool.getGroupById(group_id)

            for usuario in grupo.getGroupMembers():
                if usuario.getProperty('fullname')!="":
                    fUser.append(usuario.getProperty('fullname'))
                else:
                    fUser.append(usuario.getProperty('id'))
            return fUser
        else:
            return None


    def dameCurador(self):
        """devuelve el curador de la coleccion"""
        miColec=self.dameObjectoColeccion()
        users={'nombre':'Pato',
               'email':'eam@ad.com',
               'img':'profile.png',
               'bio':'richtext',
               'cv':'pdf profile'}
        return users

    def dameNombreColeccion(self):
        """devuelve el nombre del parent de esta coleccion"""
        result=""

        miColec=self.dameObjectoColeccion()
        if miColec:
            result=miColec.title
            return result

        return None

    def dameUriColeccion(self):
        miColec=self.dameObjectoColeccion()
        if miColec:
            return miColec.absolute_url()
        else:
            return self.context.absolute_url()

    def dameEnlaces(self):
        """devuelve el contenidos de los objetos que se encuentran dentro de la carpeta
        enlaces"""

        try:
            catalog=getToolByName(self.context,"portal_catalog")
            idF=self.context.id+'_enlace'
            ruta='/'.join(self.context[idF].getPhysicalPath())
            result=catalog(review_state='published',path={'query': ruta, 'depth': 1})
            return result
        except:
            return None

    def dameSaftyDescri(self):
        """devuelve la descripcion de la exhibicion recortada"""

        str=self.context.cuerpo.output[:900]
        cierre=str.rfind("</p>")
        apertura=str.rfind("<p>")
        if cierre<apertura:
            str=str+" ...</p>"
        return str

