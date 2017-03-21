 # -*- coding: utf-8 -*-
__author__ = 'Paul'

from zExceptions import Forbidden
from suds.client import Client
from suds.plugin import MessagePlugin

import xml.etree.ElementTree as ET

class ClienteGS(object):
    ###ruta = "%s%s%s"%(self.xmlFileBase,self.coleccion,self.xmlFileResto)###
    coleccion  =""
    bService   ="GS2MGPPSearch"
    idioma     ="en"
    urlServicio  ='http://localhost:8383/greenstone3/services/QBRSOAPServerlocalsite?wsdl'    
    error      =""        
    client     =""
    
    def __init__(self):        
        self.client= self.conectaServicio()
        pass
       
    def conectaServicio(self):
        try:
            client = Client(self.urlServicio)
        except urllib2.URLError, e:
            self.error="urlError"
            return []        
        return client 

    
    def dameListadoColecciones(self):
        ###Devuelve un listado de strings colecciones###   

        try:
            query = self.client.service.describe("","collectionList")
            query=ET.fromstring(query)
        except urllib2.URLError, e:
            self.error="urlError"
            print "error en las colecciones"
            return []        
        
        
        result=[]
        result.append("sin valor")
        for e in query.findall('.//collection'):
            result.append(e.get('name'))
            
        return result    
    
    def dameRutaXMLDeId(self,coleccion,idDoc):
        ###devuevle la bi.ruta de un idde documeento###
        self.coleccion=coleccion
        client=self.client
        res=client.service.retrieveDocumentMetadata(coleccion,self.idioma,[idDoc],['bi.ruta'])
        rtax=ET.fromstring(res)        
        if len(rtax.findall(u".//metadata[@name='bi.ruta']"))>0:
            rta=rtax.findall(u".//metadata[@name='bi.ruta']")[0]        
            return rta.text
        else:
            return ""
       
    def dameSeriesDeColeccion(self,coleccion):        
        """Devuleve un objeto con el titulo, clsificador y los lista de ids documentos hijos"""
        if self.coleccion=="":
            self.coleccion=coleccion            
        if coleccion=="sin valor":
            return []
        client=self.client
        try:
            #query =client.service.browse(self.coleccion,"",self.idioma,["CL1"],["children"])
            query = client.service.retrieveDocumentMetadata(self.coleccion,self.idioma,["CL1",],["contains"])
        except suds.WebFault, e:
            print "-------------------------"
            print e
            print "-------------------------"
            self.error=e
            return []

        series=ET.fromstring(query.encode('utf-8'))        
        subsT=series.findall('.//metadata')[0].text
        listSubs=subsT.translate(None,'"').split(";")
        f=0
        for elem in listSubs:
            listSubs[f]="CL1%s" %elem
            f+=1        

        subQuery =client.service.retrieveDocumentMetadata(self.coleccion,self.idioma,listSubs,["Title","contains"])
        subSeries=ET.fromstring(subQuery.encode('utf-8'))        
        
        resultado=[]
        subsT=subSeries.findall('.//documentNode')        
        for elem in subsT:            
            mid=elem.attrib["nodeID"]
            mtitulo=elem.find('.//metadata[@name="Title"]').text
            mdocs=elem.find('.//metadata[@name="contains"]').text.split(";")
            serie={'id'     :mid ,
                   'titulo' :mtitulo,
                   'docs'  :mdocs}
            resultado.append(serie)        
        return resultado
    
    
    def dameDocumentos(self,coleccion,docsIds):
        """Dado un listado de ids, devuelve un listado de objetos con titulo,ruta,idoc"""
        client=self.client
        metadatos=[u"ae.itemtitulo",u"ae.filetitulo",u"bi.ruta",u"SourceFile"]        
        
        
        if self.coleccion=="":
            self.coleccion=coleccion
        
        query =client.service.retrieveDocumentMetadata(self.coleccion,self.idioma,docsIds,metadatos)        
        subSeries=ET.fromstring(query.encode('utf-8'))
        
  

        subsT=subSeries.findall('.//documentNode')
        resultado=[]
        flag=0
        for elem in subsT:
            mid=elem.attrib["nodeID"]
            if elem.find('.//metadata[@name="ae.itemtitulo"]')!=None:
                mit=elem.find('.//metadata[@name="ae.itemtitulo"]').text
            else:
                mit=""
            if elem.find('.//metadata[@name="ae.filetitulo"]')!=None:
                mtitulo=elem.find('.//metadata[@name="ae.filetitulo"]').text
            else:
                mtitulo=""
            if elem.find('.//metadata[@name="bi.ruta"]')!=None:
                mruta=elem.find('.//metadata[@name="bi.ruta"]').text
            else:
                mruta="%s" %flag
            
            flag+=1
            
            serie={'id'     :mid,
                   'it'     :mit,
                   'titulo' :mtitulo,
                   'ruta'  :mruta}
            resultado.append(serie)
        return resultado


    def todasObrasDeColeccion(self,coleccion):
        ###Dada una coleccion devuelve una listado de ids de documentos###    
        self.coleccion=coleccion
        client=self.client
        listado=[]
        docsId              =client.factory.create("ArrayOf_xsd_string") 
        infoMetadatos       =client.factory.create("ArrayOf_xsd_string") 
        infoClasi           =client.factory.create("ArrayOf_xsd_string") 
        infoClasi.value     =[u"CL1"]
        
        nivelSerie=""
        nivelSubserie=""
        
        infoMetadatos.value=[u"ae.itemtitulo",u"ae.itemedicion",u"ae.itemnaturaleza",u"pr.idpreservacion",u"ae.filetitulo",u"bi.anotacion1","ae.coleccionnombreautor",u"bi.ruta"]        
   
        try:
            query =client.service.browseDescendants(self.coleccion,"",self.idioma,infoClasi)
            #query =client.service.browse(self.coleccion,"",self.idioma,["CL1"],["descendants"])
        except suds.WebFault, e:
            print "-------------------------"
            print e
            print "-------------------------"
            self.error=e
            return []

        mquery=ET.fromstring(query.encode('utf-8'))
        
        
        collectDATA=[{'conSubSeri':'boolean'},
              {'serieId':'','serieVal':'',               
               'subSList':[
                   {'subId':'',
                    'subSaval':'valor',
                    'itemList':[{'itemsId':'','itemList':''}]}
            ]}]        
        
        listClass=mquery.findall(".//classifierNode")
        nivel=0
        subR=[]
        
        CDA=[]
        
        for clN in listClass:
            if "childType" in clN.attrib.keys():
                longNanme=len(clN.attrib['nodeID'])
                
                if longNanme==5:                    
                    seriOb={'serieId':clN.attrib['nodeID'],'listSubs':[]}
                    subtmp=0                    
                    for ltmp in clN.iter("classifierNode"):    
                        subtmp+=1
                    
                    if subtmp>0:
                        #.findall(".//classifierNode")
                        for ltmp in clN.findall(".//classifierNode"):
                            if ltmp.attrib["nodeID"] not in subR:
                                subSOb={'idSub':ltmp.attrib["nodeID"],'listDocs':[]}
                                
                                for ek in ltmp.findall('.//documentNode[@nodeType="root"]'):
                                    subSOb['listDocs'].append(ek.attrib["nodeID"])           
                                    
                                seriOb['listSubs'].append(subSOb)
                    else:
                        for ek in clN.findall('.//documentNode[@nodeType="root"]'):
                                    print "docu:%s"%ek.attrib["nodeID"]
                    
                    CDA.append(seriOb)



        
        #docsIds=self.recorreDocNode(mquery)
        #docsId.value=docsIds
        #squery.find("//response/classifierNode")
        

        subQ  = client.service.retrieveDocumentMetadata(self.coleccion,self.idioma,docsId,infoMetadatos)
        squery= ET.fromstring(subQ.encode('utf-8'))

        resp  = []

        for item in squery.findall(".//documentNode"):
            tmpL=item.findall(".//metadata")
            obra={}
            if len(tmpL)>1:
                obra["id"]=item.get("nodeID")
                for noD in infoMetadatos.value:
                    obra[noD]=""
                    for elt in tmpL:
                        if noD==elt.get("name"):
                            obra[noD]=safe_unicode(elt.text)
                            break
                resp.append(obra) 
        return resp
        
    def getDescendats(self,colec):
        """devuelve una lista para armar el select"""
        re=self.todasObrasDeColeccion(colec)
        return re
        
    def getDocsFromSubSerie(self,colecName,subSerie):
        """devuelve una lista para armar el select"""
        ls=[]
        
        
        try:
            cco=self.client.service.retrieveDocumentMetadata(colecName,self.idioma,[subSerie],["contains"])
        except suds.WebFault, e:
            print "-------------------------"
            print e
            print "-------------------------"
            self.error=e
            return []
        
        
        etMeta= ET.fromstring(cco.encode('utf-8'))
        ddis=etMeta.find('.//metadata[@name="contains"]').text
        
        if ddis.find('"')>=0:
            ddis=ddis.replace('"','')        
            idsx=[]
            for elemy in ddis.split(";"):
                idsx.append(subSerie+elemy)            
            docs=self.dameDocumentos(colecName,idsx)
        else:
            docs=self.dameDocumentos(colecName,ddis.split(";"))
           
        for elem in docs:
            ls.append({"value":elem["ruta"],"title":elem["it"]})
        
        return ls
   
    def getDocsFromSerie(self,colecName,serieName):
        """devuelve una lista para armar el select"""
        series=self.dameSeriesDeColeccion(colecName)
        
        ls=[]
        ids=[]
        tmps=[]
        for elem in series:
            if elem["id"]==serieName:
              tmps=elem["docs"]              
              break;

        for ee in tmps:
            ids.append(ee.replace('"',serieName))
        
        if self.tieneSubSerie(self.coleccion):
            subSeries=self.client.service.retrieveDocumentMetadata(self.coleccion,self.idioma,ids,["Title"])
            SB= ET.fromstring(subSeries.encode('utf-8'))
            ppa=SB.findall('.//documentNode')
            ls.append({"value":"tieneSubSerie","title":"tieneSubSerie"})
            for xl in ppa:
                ls.append({'value':xl.attrib['nodeID'],'title':xl.find('.//metadata').text})
            
        else:
            docs=self.dameDocumentos(colecName,ids)
            for elem in docs:
                ls.append({"value":elem["ruta"],"title":elem["it"]})        
        return ls
        
   
    def getSeries(self,colecName):
        """devuelve una lista para armar el select"""        
        subSerieOk=self.tieneSubSerie(colecName)
        
        obras=self.dameSeriesDeColeccion(colecName)
        ls=[]
        ls.append({"value":subSerieOk,"title":subSerieOk})
        
        for elem in obras:
            ls.append({"value":elem["id"],"title":elem["titulo"]})
            
        return ls
    
    
    def tieneSubSerie(self,colecName):
        client=self.client
        
        try:
            query = client.service.browse(colecName,"",self.idioma,["CL1.1"],["children"])
        except:
            print "error buscando subSerie"
            return False
        
        mquery=ET.fromstring(query.encode('utf-8'))

        if len(mquery.findall(".//classifierNode/classifierNode"))>0:
            return True
        else:
            return False

    def recorreDocNode(self,xmlR):
        ###recorre el xml con un listado de documentos y devuelve sus IDs###
        listado=xmlR.getiterator("documentNode")
        dato=[]
        resp=[]
        for elem in listado:
            if elem.tag=="documentNode":
                dato.append(elem.get("nodeID"))

        if len(dato)<1:
            self.error="No se recuperaron registros"
            return []

        return dato
