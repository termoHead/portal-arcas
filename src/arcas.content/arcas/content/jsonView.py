__author__ = 'Paul'
from five import grok
from Products.CMFCore.interfaces import ISiteRoot
from zope.interface import Interface
from Acquisition import aq_inner, aq_parent
from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.CMFCore.utils import getToolByName
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

class JSONContentListing(View):
    """
    Called from main.js to populate the content listing view.
    """
    grok.context(Interface)
    grok.name("json_about")

    def update(self):
        self.contexto= aq_inner(self.context)


    def render(self):
        listing = self.datos_contexto()
        pretty = json.dumps(listing)
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        return pretty

    def datos_contexto(self):
        cuerpo = self.contexto.description
        if hasattr(self.contexto,"cuerpo"):
            estrin=self.contexto.cuerpo.output
            cuerpo+=estrin.encode("utf-8")
        data = dict(
            title=self.contexto.title_or_id(),
            url=self.contexto.absolute_url(),
            text=cuerpo,
            available=True,
        )
        return data

class JSONExportMenu(View):
    """
    Called from main.js to populate the content listing view.
    """
    grok.context(Interface)
    grok.name("json_menu")

    def update(self):
        self.contexto= aq_inner(self.context)

        if self.request.form.has_key("idC"):
            idColeccion=self.request.form["idC"]



    def render(self):
        listing = self.datos_contexto()
        pretty = json.dumps(listing)
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        return pretty

    def datos_contexto(self):
        catalogo=getToolByName(self.contexto,"portal_catalog")

        fpA="/".join(self.contexto.getPhysicalPath())
        colecFolder=catalogo.searchResults(path={ "query": fpA,'depth': 1},sort_on='getObjPositionInParent')
        result=[]

        for exhi in colecFolder:
            if not exhi.exclude_from_nav:
                data={'url':exhi.getURL(),'titulo':exhi.Title}
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