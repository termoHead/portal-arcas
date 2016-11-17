# -*- coding: utf-8 -*-
__author__ = 'Paul'
#"lucene-jdbm-demo",

import os
from zExceptions import Forbidden
from suds.client import Client
from suds.plugin import MessagePlugin
import urllib2
import xml.etree.ElementTree as ET
from plone.autoform import directives

from Products.CMFPlone.utils import safe_unicode

"""

    Simple sample form

"""
from five import grok
from plone.directives import form

from zope import schema
from z3c.form import button
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE, INPUT_MODE
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import action
from zope.component import getMultiAdapter
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import directlyProvides
from plone.supermodel import model
import xml.etree.ElementTree as ET

    

ppo_vocab=SimpleVocabulary([])


def coleccionesVocab(context):
    "colecciones en "
    cl=ClienteGS()    
    terms = []      
    return SimpleVocabulary.fromValues(cl.dameListadoColecciones())


directlyProvides(coleccionesVocab, IContextSourceBinder)


class IGsMetaItem(form.Schema):
    model.fieldset('Serie',
        label=(u"Metadatos del Item"),
        fields=["f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones","f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta"]
    )
    f_fechaCreacion= schema.TextLine(
        title=u"Fecha",
        description=u"Fecha de creacion del documento",
        required=False,
    )
    f_lugarCreacion= schema.TextLine(
        title=u"Lugar",
        description=u"Lugar de creacion del documento",
        required=False,
    )
    f_descFisica= schema.TextLine(
        title=u"Descripción física",
        description=u"Descripción física del documento",
        required=False,
    )
    f_dimensiones= schema.TextLine(
        title=u"Dimensiones",        
        required=False,
    )
    f_idioma= schema.TextLine(
        title=u"Idioma",        
        required=False,
    )
    f_naturaleza= schema.TextLine(
        title=u"Naturaleza",
        description=u"Naturaleza del documento",
        required=False,
    )
    
    f_alcance= schema.TextLine(
        title=u"Alcance",        
        required=False,
    )
    directives.mode(f_ruta='hidden')
    f_ruta= schema.TextLine(
        title=u"Ruta al xml",
        description=u"no se que es... sera el título del documento",
        required=False,
    ) 
    form.widget('f_anotacion', klass='recargaForm',size=5)
    f_anotacion = schema.Text(title=u"Editar Metadato",required=False,)


class IGsMetaSerie(form.Schema):
    model.fieldset('Item',
        label=(u"Metadatos de la serie"),
        fields=["s_titulo","s_temporal","s_extension","s_dimension","s_creador","s_colaborador","s_caracteristicas","s_alcance","s_lenguaiso","s_ediciones"]
    )
    s_titulo= schema.TextLine(title=u"Titulo",
        description=u"no se que es... sera el título del documento",required=False,) 
    s_temporal= schema.TextLine(title=u"Extensión Temporal",
        description=u"no se que es... sera el título del documento",required=False,) 
    s_extension= schema.TextLine(title=u"Extensión",
        description=u"no se que es... sera el título del documento",required=False,) 
    s_dimension= schema.TextLine(title=u"Dimensiones",
        description=u"no se que es... sera el título del documento",required=False,)             
    s_creador= schema.TextLine(title=u"Creador",
        description=u"no se que es... sera el título del documento",required=False,)
    s_colaborador= schema.TextLine(title=u"Creador",
        description=u"no se que es... sera el título del documento",required=False,)
    s_caracteristicas= schema.TextLine(title=u"Caracteristicas",
        description=u"no se que es... sera el título del documento",required=False,)
    s_alcance= schema.TextLine(title=u"Alcance",
        description=u"no se que es... sera el título del documento",required=False,)
    s_lenguaiso= schema.TextLine(title=u"Idioma",
        description=u"no se que es... sera el título del documento",required=False,)            
    s_ediciones= schema.TextLine(title=u"Ediciones",
        description=u"no se que es... sera el título del documento",required=False,)            
                





























class IEditGS(form.Schema, IGsMetaItem, IGsMetaSerie ):
    """Campos del formulario de edición de un documento Greenston3 en el import!"""    
    model.fieldset('Datos',
        label=(u"Datos de la Obra"),
        fields=["coleccion","serie","obra","obraTmp"]
    )
    
    form.widget('coleccion', klass='recargaForm')
    coleccion= schema.Choice(
        title=u"Colección",
        description=u"Elija una colección para editar",
        source=coleccionesVocab,        
        required=True,
    )
    serie = schema.Choice(
        title=u"Serie",
        description=u"Elija una obra para editar",        
        vocabulary=ppo_vocab,
        required=False,
    )
    obra = schema.Choice(
        title=u"Obra",
        description=u"Elija una obra para editar",        
        vocabulary=ppo_vocab,
        required=False,
    )
    directives.mode(obraTmp='hidden')
    obraTmp= schema.TextLine(
        title=u"obraTmp",
        description=u"una pavada",
        required=False,
    ) 
    

class EditGS(form.SchemaForm):
    """
       Edita un documento de Greenstone3 desde el import!
    """
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'
    

    grok.name('editGs')
    #grok.require('zope2.View')
    grok.require('cmf.ListFolderContents')    
    grok.context(ISiteRoot)    
    schema = IEditGS
    ignoreContext = True

    label = u"Editando un Documento GS"
    description = u"Solo modificación de anotacion"
    fsmanager=""
    coleccion="cordemia"
    serie=""
    obra=""
    
    
    
    
    lsw=["f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones","f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta"]
    
    infoMetadatosSerie={'s_titulo':'ae.filetitulo',
                's_temporal':'ae.fileCoberturatemporal',
                's_extension':'ae.fileextension',
                's_dimension':'ae.filedimension',
                's_creador':'ae.filecreator',
                's_colaborador':'ae.filecolaborator',
                's_caracteristicas':'ae.filecaracteristicastecnicas',
                's_alcance':'ae.filealcance',
                's_lenguaiso':'ae.filelenguaiso',
                's_ediciones':'ae.fileediciones'
    }
    infoMetadatoSubSerie={}
    infoMetaItem={ 'f_fechaCreacion':'ae.itemcoberturatemporal', 
                    'f_lugarCreacion':'bi.lugar',
                    'f_descFisica':'ae.itemdescripcionfisica',
                    'f_dimensiones':'ae.itemdimension',
                    'f_idioma':'ae.itemlenguaiso',
                    'f_naturaleza':'ae.itemnaturaleza',
                    'f_alcance':'ae.itemalcance',
                    'f_anotacion':'bi.anotacionitem',
                    'f_ruta':'bi.ruta'}

    
    editOk=False    
    step1=["serie"]
    step2=["obra"]    
    
    
    
    @property
    def mmi_vocab(self):
        cl=ClienteGS()
        lista=cl.getSeries(self.coleccion)
        terms=[SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]) for pair in lista ]        
        return SimpleVocabulary(terms)
    
    @property
    def mmo_vocab(self):
        cl=ClienteGS()
        lista=cl.getDocsFromSerie(self.coleccion,self.serie)
        terms=[SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]) for pair in lista ]
        return SimpleVocabulary(terms)
    
    
    def update(self):        
        super(EditGS, self).update()
    
    
    def updateWidgets(self):                
        super(EditGS, self).updateWidgets()        


    def showObras(self):
        # Set a custom widget for a field for this form instance only
        
        
        if self.groups[1].widgets["f_ruta"].value!=u"":
            return True
        else:
            return False


    def showSave(self):
        if "form.buttons.editar" in self.request.form:
            return True
        else:
            return False

   
    @button.buttonAndHandler(u'Editar',condition=showObras)
    def editHandler(self, action):
        """Recupera el METADA XML y lo carga en la planilla"""
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        infoMetadatos=self.infoMetadatosSerie

        ruta=self.xmlFileBase+self.widgets["coleccion"].value[0]+"/"+self.widgets["obraTmp"].value        

        # Do something with valid data here
        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)
        self.editOk=True
        self.fsmanager=FSManager()
        archivo=self.fsmanager.openF(ruta,self.widgets["coleccion"].value[0])
        if archivo['error']!=u"":
            self.status = u"No se encontró el archivo"
            return 
        
        
        for v in infoMetadatos:
            metaValue=self.fsmanager.dameMetadata(infoMetadatos[v])
            self.widgets[v].value=metaValue
        self.status = "Articulo encontrado"

    @button.buttonAndHandler(u'Guardar',condition=showObras)
    def saveHandler(self, action):  
        infoMetadatos=self.infoMetadatosSerie
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        dicDatos={
            "version":"1",
            "idColec":self.widgets["coleccion"].value[0],
            "ruta":self.widgets["ruta"].value,            
            "metadatos":[(x,self.widgets[infoMetadatos[x]].value) for x in infoMetadatos]}
        
        self.fsmanager=FSManager()
        if self.fsmanager.saveFile(dicDatos):
            self.status =u"CambiosDefine Form handling guardados... mail to M. Pichinini!"
        else:
            self.status =u"No se pueden guardar los cambios... generando reporte"

    @button.buttonAndHandler(u"Cancel",condition=showObras)
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page.
        """
        self.status = "Cambios cancelados"
        self.editOk=False


class FSManager:
    
    """
        Abre el archivo y lo guarda en miXml
        gsx=FSManager()
        fileOk=gsx.openF(ruta, coleccion)
        if fileOk==False:
            print "error:%s"%gsx.erromMsj
            return            
            
        fileXml=gsx.miXml
        
        
    """
    erromMsj=""
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'    
    miXml=""
    
    def openF(self,ruta,coll):
        #if ruta.find("web")==-1:
        #    self.xmlFileResto=ruta.split(coll)[1]
        ruta=self.xmlFileBase+coll+"/"+ruta
        result=self.openFile(ruta) 
        
        return result
                
    def openFile(self, ruta):
        try:
            xmlFile = ET.parse(ruta)
            self.miXml=xmlFile
            print "ok"
            return True
        
        except ET.ParseError:
            print("failure")
            print("last successful: {0}".format(last))
            self.erromMsj={"error":u"Error de parseo"}
            
        except:
            print("catastrophic failure")
            self.erromMsj={"error":u"No se encontró el archivo"}

        return False


    def dameSigVerison(self,carpeta):
        listado =os.listdir(carpeta)
        tmp     =["1"]
        listR=[]
        for elem in listado:   
            fx="metadata"
            ex=".xml"
            if elem.find(ex)>-1 and elem.find(fx)>-1:
                version=elem[len(fx):elem.find(ex)]
                listR.append(version)

        if len(listR)==0:
            return "1"
        
        listR.sort()
        nex=listR[-1]
        resultado = str(int(nex[1:])+1)
        return resultado
        
    def saveFile(self,obModificado):
        """guarda los datos en el xml"""
        pathFolder      =self.xmlFileBase+obModificado["idColec"]+self.xmlFileResto
        version         =self.dameSigVerison(pathFolder)
        newfilename     =self.xmlFileBase+obModificado["idColec"]+self.xmlFileResto+"metadataV"+version+".xml"
        rm              =self.openF(obModificado["ruta"],obModificado["idColec"])
        
        if rm["error"]!="":
            return False

        for met in obModificado["metadatos"]:
            try:
                self.miXml.findall('.//Metadata[@name="'+met[0]+'"]')[0].text=met[1]
            except:
                print "no pude guardar el metadato %s > %s" %(met[0],met[1])
        try:
            self.miXml.write(newfilename,encoding="UTF-8", xml_declaration=True)
        except:
            print "problema guardando el archivo"
        return True
        
    def dameMetadata(self,strMeta):
        try:
            root = self.miXml.getroot()
        except e:
            print "no se puede parsear el xml"
            return []
        
        metadato=""
        if len(self.miXml.findall(u'.//Metadata[@name="'+strMeta+'"]'))>0:
            meta=self.miXml.findall(u'.//Metadata[@name="'+strMeta+'"]')[0].text
            metadato=meta
            
        return metadato
    


    
    
    def getMetadataForItem(self):
        """Metodo que devuelve un diccionario de METADATOS ITEMS para json"""        
        res=self.getMetadataFor(EditGS.infoMetaItem)        
        return res
    
    def getMetadataForSubSerie(self):
        """Metodo que devuelve un diccionario de METADATOS SUBSERIE para json"""
        res=self.getMetadataFor(EditGS.infoMetadatoSubSerie)        
        return res
    
    def getMetadataForSerie(self):
        """Metodo que devuelve un diccionario de METADATOS SERIE para json"""
        res=self.getMetadataFor(EditGS.infoMetadatosSerie)        
        return res
    
    def getMetadataFor(self,infoMetadatos):
        """METODO AUXILIAR PARA DEVOLVER METADATOS EN EL DICIONARIO infoMetadatos,infoMetadatoSubSerie,infoMetaItem de EditGS"""
        res=[]
        for ke,val in infoMetadatos.items():
            res.append({val:self.dameMetadata(val)})
        return res
    
class ClienteGS:
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
        query = self.client.service.describe("","collectionList")
        query=ET.fromstring(query)
        result=[]
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
        metadatos=[u"ae.itemtitulo",u"ae.filetitulo",u"bi.ruta"]        
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
    
    def dame(self,coleccion):        
        serieM=client.service.retrieveDocumentMetadata(coleccion,self.idioma,subS)
        serieMX==ET.fromstring(serieM.encode('utf-8'))
        arr=ppx.findall(".//metadata[@name='Title']")
        resp=[]
        for nodo in arr:
            resp.append(nodo.attrib["Title"])
            
        return  resp


    """def todasObrasDeColeccion(self,coleccion):
        ###Dada una coleccion devuelve una listado de ids de documentos###    
        self.coleccion=coleccion
        client=self.client
        listado=[]
        docsId              =client.factory.create("ArrayOf_xsd_string") 
        infoMetadatos       =client.factory.create("ArrayOf_xsd_string") 
        infoClasi           =client.factory.create("ArrayOf_xsd_string") 
        infoClasi.value     =[u"CL1"]
        
        infoMetadatos.value=[u"ae.itemtitulo",u"ae.itemedicion",u"ae.itemnaturaleza",u"pr.idpreservacion",u"ae.filetitulo",u"bi.anotacion1","ae.coleccionnombreautor",u"bi.ruta"]        
   
        try:
            #query =client.service.browseDescendants(self.coleccion,"",self.idioma,infoClasi)
            query =client.service.browse(self.coleccion,"",self.idioma,["CL1"],["descendants"])
        except suds.WebFault, e:
            print "-------------------------"
            print e
            print "-------------------------"
            self.error=e
            return []

        mquery=ET.fromstring(query.encode('utf-8'))
        docsIds=self.recorreDocNode(mquery)
        docsId.value=docsIds
        
        subQ=client.service.retrieveDocumentMetadata(self.coleccion,self.idioma,docsId,infoMetadatos)
        
        squery=ET.fromstring(subQ.encode('utf-8'))
        resp=[]
        
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
        """
   
   
    def getDocsFromSerie(self,colecName,serieName):
        """devuelve una lista para armar el select"""
        series=self.dameSeriesDeColeccion(colecName)
        ls=[]
        ids=[]        
        for elem in series:
            if elem["id"]==serieName:
              ids=elem["docs"]  
              break;
          
        
        docs=self.dameDocumentos(colecName,ids)
        for elem in docs:
            
            ls.append({"value":elem["ruta"],"title":elem["it"]}) 
        
        return ls
        
   
    def getSeries(self,colecName):
        """devuelve una lista para armar el select"""        
        obras=self.dameSeriesDeColeccion(colecName)        
        ls=[]
        for elem in obras:
            ls.append({"value":elem["id"],"title":elem["titulo"]})                            
        return ls
    
    


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

     

        
    