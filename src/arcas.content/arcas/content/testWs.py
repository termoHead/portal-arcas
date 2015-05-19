# -*- coding: utf-8 -*-
__author__ = 'Paul'
#"lucene-jdbm-demo",
from zope.interface import Interface
from zope.schema import Text, TextLine, Field
from zope.component import getMultiAdapter
from zExceptions import Forbidden
from suds.client import Client
from Products.Five.browser import BrowserView
import suds
import urllib2
import codecs
from suds.xsd.doctor import ImportDoctor, Import
from suds.plugin import MessagePlugin
from Products.CMFPlone.utils import safe_unicode
import xml.etree.ElementTree as ET
from arcas.content.config import *

class UnicodeFilter(MessagePlugin):
    def received(self, context):

        #decoded  = unicode(context.reply.strip(codecs.BOM_UTF8), 'utf-8')
        decoded = safe_unicode(context.reply)
        reencoded = decoded.encode('utf-8')

        context.reply = reencoded

class ITestWs(Interface):
    """This is the book mark object."""

class TestWs(BrowserView):
    def __init__(self, context, request, base_url=''):
        self.context    =context
        self.request    =request
        self.base_url   =base_url
        #self.coleccion ="puig"
        self.coleccion  ="puig"
        self.bService   ="GS2MGPPSearch"
        self.idioma     ="en"
        self.url        ='http://localhost:8383/greenstone3/services/QBRSOAPServerlocalsite?wsdl'
        self.error      =""

    def __call__(self, *args, **kwargs):
        self.update()
        return self.index()


    def update(self):
        """ Hide the editable-object border """
        self.request.set('disable_border', True)
        self.consulta=""
        if 'buscaTexto' in self.request.form:
            authenticator = getMultiAdapter((self.context, self.request), name=u"authenticator")
            #if not authenticator.verify():
            #    raise Forbidden()

        self.textoBuscado   =self.request.form.get('buscaTexto') or None
        self.coleccion      =self.request.form.get('idColec') or self.coleccion

        if self.textoBuscado:
            self.resultadoConsulta=self.buscaTexto()

    def coleccionName(self):
        """devuelve las palabras que es"""
        if self.coleccion:
            return self.coleccion
        else:
            return ""

    def damCodes(self):
        """Devuelve una lista"""
        return ("pp","ppepe","peron")

    def dameRutaDocGS(self):
        """Devuelve la ruta al registro en greenstone"""
        return URL_GREENSTON_DOC+self.coleccion+"/document"
   

    def buscaTexto(self):
        #client = Client(self.url,plugins=[UnicodeFilter()])
        try:
            client = Client(self.url)
        except urllib2.URLError, e:
            self.error="urlError"
            return []
        infoParams=client.factory.create("ArrayOf_xsd_string")
        infoParamsA=client.factory.create("ArrayOf_xsd_string")
        infoParamsB=client.factory.create("ArrayOf_xsd_string")


        infoParams.value=[self.textoBuscado]
        ##textos="(q,"++")"

        import pdb
        pdb.set_trace()
        
        try:
            query = client.service.basicQuery(self.coleccion,self.idioma,self.textoBuscado)
        except suds.WebFault, e:
            print e
            self.error=e
            return []


        #query = client.service.retrieveDocumentContent(self.coleccion,self.idioma,infoParams)
        xmlR=ET.fromstring(query.encode('utf-8'))
        listado=xmlR.getiterator("documentNode")

        dato=[]
        resp=[]
        for elem in listado:
            if elem.tag=="documentNode":
                dato.append(elem.get("nodeID"))

        if len(dato)<1:
            self.error="No se recuperaron registros"
            return []

        #infoParamsA.value=["HASH01c1e185ed45f82b1921620a"]
        infoParamsA.value=dato
        #subQ=client.service.retrieveDocumentContent(self.coleccion,self.idioma,infoParamsA) u"ae.filetitulo",u"ae.fileenlace",u"ae.itemtitulo",u"bi.anotacion1"
        infoParamsB.value=[u"pr.idpreservacion",u"ae.filetitulo",u"bi.anotacion1"]
        try:
            subQ=client.service.retrieveDocumentMetadata(self.coleccion,self.idioma,infoParamsA,infoParamsB)
            xmlTmp=ET.fromstring(subQ.encode('utf-8','replace'))
        except Exception, e:
            print e
            self.error=e
            return []



        for item in xmlTmp.getiterator():
            if item.tag=="documentNode":
                itemML=item.getchildren()[0]
                itemMD=itemML.getchildren()[0]
                itemMDTitu=itemML.getchildren()[1]
                itemMDTexto=itemML.getchildren()[2]
                dato=itemMDTexto.text
                if itemMD.tag=="metadata":
                    resp.append({
                        'hash':item.get("nodeID"),
                        'preserva':itemMD.text,
                        'titulo':itemMDTitu.text,
                        'texto':safe_unicode(dato)
                    })

        return resp


    def dameColecciones(self,cliente):
        """Devuelve el listado de collecciones en GS3"""
        query = client.service.describe(self.coleccion,"collectionList")


    def listMarks(self):
        client = Client(self.url)
        classifierNodeIDs = client.factory.create("ArrayOf_xsd_string")
        classifierNodeIDs.value = ["CL1","CL1.1","CL1.1.1"]

        structureParams=client.factory.create("ArrayOf_xsd_string")
        structureParams.value =["ancestors","children"]

        infoParams=client.factory.create("ArrayOf_xsd_string")
        infoParams.value =["numSiblings"]
		
        servicios = client.service.browse(self.coleccion,self.bService,self.idioma,classifierNodeIDs,structureParams,infoParams)

        return servicios
		
		
class Hashmap(object):
    """
    character holding hash map
    """
    def __init__(self, hash_fn, length=100):
        assert hasattr(hash_fn, '__call__'), 'You must provide a hash function'

        self._buckets = [None] * length
        self.hash_len = length
        self.hash_fn = hash_fn

        # Max items per bucket
        self.change_len = length / 5

    def _hash(self, key):
        return self.hash_fn(key) % self.hash_len

    def put(self, key, val):
        pos = self._hash(key)
        bucket = self._buckets[pos]
    
        if bucket is None:
            self._buckets[pos] = bucket = LinkedList()
            bucket.put(key, val)
        else:
            bucket.put(key, val)
            if len(bucket) >= self.change_len:
                #print 'growing', 'num buckets: ', len(self._buckets)
                self._grow()

    def _grow(self):
        # Double size of buckets
        self.hash_len = self.hash_len * 2

        # New max len for buckets
        self.change_len = self.hash_len / 5

        # new bucket holder
        oldBuckets = self._buckets
        self._buckets = [None] * self.hash_len


        # Iterate through all buckets
        # and reinsert key=>vals
        for bucket in oldBuckets:
            if bucket is None: continue
            for (key, val) in bucket:
                self.put(key, val)


    def get(self, key):
        pos = self._hash(key)
        bucket = self._buckets[pos]

        if bucket is None: return None

        return bucket.get(key)

    def delete(self, key):
        """
        Deletes a value in a hashmap
        returns the value in the map if it exists
        """
        pos = self._hash(key)
        node = self._buckets[pos]

        if node is None: return None

        self._buckets[pos] = None
        self.num_vals -= 1

        return node.val


    def _shrink(self):
        #length = self.hash_len 
        pass
        
    def __repr__(self):
        return '<Hashmap %r>' % self._buckets
    
    def __len__(self):
        n = 0
        for bucket in self._buckets:
            if bucket is None: continue
            n += len(bucket)
        return n

    def get_num_empty_buckets(self):
        n = 0
        for bucket in self._buckets:
            if bucket is None or len(bucket) == 0: n += 1
        return n

    def get_longest_bucket(self):
        longest = 0
        b = None
        for bucket in self._buckets:
            if bucket is None: continue

            l = len(bucket)
            if longest < l:
                longest = l
                b = bucket
        return longest

    def get_shortest_bucket(self):
        shortest = 0
        b = None
        for bucket in self._buckets:

            if bucket is None:
                shortest = 0
                b = None
                break

            l = len(bucket)
            if shortest == 0: shortest = l
            if shortest >= l:
                shortest = l
                b = bucket

        return shortest