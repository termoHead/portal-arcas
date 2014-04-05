# -*- coding: utf-8 -*-
__author__ = 'Paul'
import random
from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter
from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import\
    ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.memoize.compress import xhtml_compress
from arcas.content.coleccionesFolder import IColeccionesFolder
from arcas.content.coleccion import IColeccion
from zope.site.hooks import getSite
import unicodedata

from Acquisition import aq_parent,aq_base,aq_inner

from OFS.interfaces import IOrderedContainer



class IColeccionPortlest(IPortletDataProvider):
    """Marker para el portlet"""


class Assignment(base.Assignment):
    implements(IColeccionPortlest)

    def __init__(self):
        pass

    @property
    def title(self):
        cadena="Colecciones home"
        return cadena


class Renderer(base.Renderer):
    ##_template = ViewPageTemplateFile('intereses_portlet.pt')
    render = ViewPageTemplateFile('colecciones_portlet.pt')


    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        self.anonymous = portal_state.anonymous()
        self.portal_url = portal_state.portal_url()
        self.typesToShow = portal_state.friendly_types()

        plone_tools = getMultiAdapter((context, self.request), name=u'plone_tools')
        self.catalog = plone_tools.catalog()
        self.portal = getMultiAdapter((self.context, self.request),
            name=u'plone_portal_state').portal()

    @property
    def available(self):
        items=self.getColecciones()
        return items is not None


    @memoize
    def getColecciones(self):
        ##recreaFolder= self.getContainer(folder.encode('utf8'))
        ##cuando busca documento hace referencia al campo "documento" que es el destacado del directorio

        try:
            colList=self.catalog(portal_type='arcas.coleccion',review_state='Publicado')
            resuList=[]
            extraFUrl=""
            extraFT=""

            for elem in colList:
                destacado=self.context.unrestrictedTraverse(elem.getPath())


                for carpeta in destacado.getFolderContents():
                    if carpeta.portal_type=="Folder" and carpeta.Title!="Galería":
                        extraFUrl=carpeta.getURL()
                        extraFT=carpeta.Title
                        break

                resuList.append({
                    "titulo":elem.Title,
                    "url":elem.getURL(),
                    "description":elem.Description,
                    "extraFolderUrl":extraFUrl,
                    "extraFolderTitulo":extraFT
                }
                )
                return resuList
        except :
            print "no hay exhibiciones asiganadas al portlet"
            pass

        return None

    def getBgImg(self):
        """Devuelve un string para conformar el src de un imagen"""
        ppUrl=self.getDestacado().absolute_url()
        ppo  =ppUrl+"/@@images/bgCabezalHome"
        return ppo

    def listColeccUrl(self):
        """Devuelve la url al listado de exhibiciones"""
        exlis=self.catalog(object_provides=IColeccionesFolder.__identifier__)
        if len(exlis)>0:
            return exlis[0].getURL()
        else:
            return False



class AddForm(base.AddForm):
    form_fields = form.Fields(IColeccionPortlest)
    label = u"Add Recent Portlet"
    description = u"This portlet displays recently modified content."

    def create(self, data):
        return Assignment()

class EditForm(base.EditForm):
    form_fields = form.Fields(IColeccionPortlest)
    label = u"Edit Recent Portlet"
    description = u"this portlet displays recently modified content."

