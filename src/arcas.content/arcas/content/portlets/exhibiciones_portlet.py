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


from zope.site.hooks import getSite
import unicodedata

from Acquisition import aq_parent,aq_base,aq_inner

from OFS.interfaces import IOrderedContainer
from arcas.content.utils import ColeccionUtils


class IExhibPortlet(IPortletDataProvider):
    canal = schema.Choice(
        title=u"Canal",
        vocabulary='arcas.ExhibicionesVocab',
    )

class Assignment(base.Assignment):
    implements(IExhibPortlet)

    def __init__(self, canal=[]):
        self.canal = canal

    @property
    def title(self):
        cadena=""
        try:
            cadena="Exhibicion Destacada: "+self.data.canal.split("/")[-1]
        except :
            cadena="Exhibicion Destacada"
        return cadena


class Renderer(base.Renderer):
    ##_template = ViewPageTemplateFile('intereses_portlet.pt')
    render = ViewPageTemplateFile('exhibiciones_portlet.pt')


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
        items=self.getDestacado()
        return items is not None


    @memoize
    def getDestacado(self):
        ##recreaFolder= self.getContainer(folder.encode('utf8'))
        ##cuando busca documento hace referencia al campo "documento" que es el destacado del directorio


        try:
            if self.data.canal:
                destacado=self.context.unrestrictedTraverse(self.data.canal)
                colecTRelated=destacado.coleccionR.to_object
                colecUtils=ColeccionUtils(colecTRelated)
                resp={
                    'titulo' : destacado.title,
                    'descri' : destacado.description,
                    'exhiurl': destacado.absolute_url(),
                    'curador': colecUtils.dameCurador(),#esta dameCurador funcion ya devuelve una lista,
                    'integrantes': colecUtils.getCoordinadores()+colecUtils.dameIntegrantes()
                }

                return resp
        except :
            print "no hay exhibiciones asiganadas al portlet"
            pass

        return []

    def getBgImg(self):
        """Devuelve un string para conformar el src de un imagen"""
        ppUrl=self.getDestacado().absolute_url()
        ppo  =ppUrl+"/@@images/bgCabezalHome"
        return ppo

    def listExhiUrl(self):
        """Devuelve la url al listado de exhibiciones"""
        from arcas.content.exhibicionesFolder import IExhibicionesFolder
        exlis=self.catalog(object_provides=IExhibicionesFolder.__identifier__)
        if len(exlis)>0:
            return exlis[0].getURL()
        else:
            return False



class AddForm(base.AddForm):
    form_fields = form.Fields(IExhibPortlet)
    label = u"Add Recent Portlet"
    description = u"This portlet displays recently modified content."

    def create(self, data):
        return Assignment(canal=data.get('canal',[]))

class EditForm(base.EditForm):
    form_fields = form.Fields(IExhibPortlet)
    label = u"Edit Recent Portlet"
    description = u"this portlet displays recently modified content."
