# -*- coding: utf-8 -*-
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
from arcas.content.editGS import ClienteGS
from arcas.content.editGS import FSManager

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

class JSONGS_WS(View):
    """
    Devuleve un listado json de  documentos o fuente
    /json_gs?series=puig
    /json_gs?docs=boquitas pintadas
    """
    grok.context(Interface)
    grok.name("json_gs")

    def update(self):
        self.contexto= aq_inner(self.context)
        self.cli=ClienteGS()
        
        if "series" in self.request.form:
            self.coleccion  =self.request.form["series"]
            self.metodo     ="getSeries"
            self.valor      =self.request.form["series"]
            
        if "docs" in self.request.form:
            self.metodo     ="getDocs"
            self.coleccion  =self.request.form["coleccion"]
            self.valor      =self.request.form["docs"]

        if "ruta" in self.request.form:
            self.metodo     ="getMetadata"
            self.ruta       =self.request.form["ruta"]
            self.coleccion  =self.request.form["coleccion"]
            self.valor      =self.request.form["docs"]
            self.tienSub   =self.request.form["subserie"]
            
        elif "subserie" in self.request.form:
            self.metodo     ="getSubSeries"
            self.coleccion  =self.request.form["coleccion"]            
            self.valor      =self.request.form["subserie"]

    def render(self):
        #re=self.dameCL1()
        #return re
        if self.metodo=="getSeries":
            listing=self.dameSeries()
        elif self.metodo=="getDocs":
            listing=self.dameFuentes()
        elif self.metodo=="getSubSeries":
            listing=self.dameSubSeries()
        else:
            listing=self.dameMetadatos()
        
        return self.empaqueta(listing)


    def empaqueta(self,listing):
        """empaqueta para relegar"""
        pretty = json.dumps(listing)
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        return pretty

    def getSourceObra(self):
        listing=self.dameObras()
        return empaquetaObra()
    
    def dameFuentes(self):
        """Devuleve todas las obras de la serie"""        
        docs=self.cli.getDocsFromSerie(self.coleccion,self.valor)
        return docs
    
    def dameSubSeries(self):
        """Devuelve todas las obras de una subSerie"""
        obras=self.cli.getDocsFromSubSerie(self.coleccion,self.valor)
        return obras
    
        
    def dameSeries(self):
        """Devuelve todas las series de una coleccion"""        
        obras=self.cli.getSeries(self.valor)        
        return obras
    
    
    def dameCL1(self):
        """Devuelve todas las series de una coleccion"""
        docs=self.cli.getDescendats(self.coleccion)

    def dameMetadatos(self):
        """Devuelve todas las series de una coleccion"""
        result={"serieMetadata":"","subserieMetadata":"","itemMetadata":""}             

        if self.tienSub:        
            subSerieOk=True
        else:
            subSerieOk=False
            
        if subSerieOk:
            rutaItem=self.ruta
            
            arTmp = rutaItem.split("/")
            del arTmp[-2]
            del arTmp[-2]
            rutaSerie = "/".join(arTmp)
            
            arTmp = rutaItem.split("/")         
            del arTmp[-2]
            rutaSubSerie = "/".join(arTmp)            
            
        else:
            arTmp = rutaItem.split("/")            
            del arTmp[-2]
            rutaSerie = "/".join(arTmp)    

        manageFS  = FSManager()
        obraF     = manageFS.openF(rutaItem,self.coleccion)
        
        if type(obraF) != type(True):
            result["itemMetadata"]="error"
        else:
            result["itemMetadata"] = manageFS.getMetadataForItem()

            
            
            
            
            
            
            
            
        serieF=manageFS.openF(rutaSerie,self.coleccion)        
        

        if type(serieF) != type(True):
            result["serieMetadata"] = "error"
        else:
            result["serieMetadata"] = manageFS.getMetadataForSerie()

        if subSerieOk:                        
            serieSubF = manageFS.openF(rutaSubSerie,self.coleccion)
            if type(serieSubF) != type(True):
                result["subserieMetadata"] = "error"
            else:        
                result["subserieMetadata"] = manageFS.getMetadataForSubSerie()
        



        return result


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

class JSONAutenticado(View):
    """
    Called from main.js to populate the content listing view.
    """
    grok.context(Interface)
    grok.name("json_autenticado")
	
    def update(self):
        self.contexto= aq_inner(self.context)

    def render(self):
        listing = self.datos()
        pretty = json.dumps(listing)
        self.request.response.setHeader("Content-type", "application/json")
        self.request.response.setHeader('Access-Control-Allow-Origin', '*')
        return pretty

    def datos(self):
        sdm = self.context.session_data_manager
        session_id = sdm.getSessionData(create=False)
        return [{'id':session_id}]

class JSONExportMenu(View):
    """
    Called from main.js to populate the content listing view.
    """
    grok.context(Interface)
    grok.name("json_menu")

    def update(self):
        self.contexto = aq_inner(self.context)

        if self.request.form.has_key("idC"):
            idColeportadaccion=self.request.form["idC"]

    def render(self):
        listing = self.datos_contexto();
        pretty  = json.dumps(listing);
        self.request.response.setHeader("Content-type", "application/json");
        self.request.response.setHeader('Access-Control-Allow-Origin', '*');
        return pretty;

    def datos_contexto(self):
        catalogo=getToolByName(self.contexto,"portal_catalog")

        fpA="/".join(self.contexto.getPhysicalPath())
        colecFolder=catalogo.searchResults(path={ "query": fpA,'depth': 1},sort_on='getObjPositionInParent')
        result=[]

        for exhi in colecFolder:
            if not exhi.exclude_from_nav:
                data={'url':exhi.getURL(),'titulo':exhi.Title};
                result.append(data);
        return result

    def emptyData(self):
        data = dict(
            title="",
            url="",
            text="",
            available=False,
        )
        return data
