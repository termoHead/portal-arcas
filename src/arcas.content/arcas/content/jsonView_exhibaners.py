__author__ = 'Paul'
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from zope.interface import Interface
from Acquisition import aq_inner, aq_parent
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
from arcas.content.utils import ColeccionUtils
import json
try:
    from five.grok import CodeView as View
except ImportError:
    from five.grok import View
import socket
import urllib
import urllib2
from urllib2 import HTTPError
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class JSONExhibicionesList(View):
    """
    Called from main.js to populate the content listing view.
    """
    grok.context(Interface)
    grok.name("json_exhibiciones")

    def update(self):
        self.contexto= aq_inner(self.context)
        idColeccion="puig"
        if self.request.form.has_key("idC"):
            idColeccion=self.request.form["idC"]

        self.idColeccion=idColeccion

    def render(self):
        listing = self.datos_contexto()
        pretty = json.dumps(listing)
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        return pretty

    def datos_contexto(self):
        catalogo=getToolByName(self.contexto,"portal_catalog")
        colecFolder=catalogo.searchResults(portal_type="arcas.coleccionesFolder")

        if len(colecFolder)<1:
            return self.emptyData()

        miColeccion=""

        colectFolder=self.context.unrestrictedTraverse(colecFolder[0].getPath())
        desta_path = '/'.join(colectFolder.getPhysicalPath())
        cataloDest=catalog.searchResults(path={'query':desta_path , 'depth': 1})

        for coleccion in cataloDest:
            colecObj=self.context.unrestrictedTraverse(coleccion.getPath())
            if colecObj.GS_ID==self.idColeccion:
                miColeccion=colecObj
                break

        if miColeccion=="":
            return self.emptyData()

        utilidad= ColeccionUtils(miColeccion)
        result=[]

        for exhi in utilidad.dameExhibicionesR():
            data={'url':exhi.absolute_url()+'/images/baner','titulo':exhi.title,'remoteURL':exhi.absolute_url()}
            result.append(data)
        return result

    def emptyData(self):
        data = dict(
            title="",
            url="",
            text="",
            available=False,
        )
        return data