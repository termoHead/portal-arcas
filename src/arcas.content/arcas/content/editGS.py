# -*- coding: utf-8 -*-
__author__ = 'Paul'
#"lucene-jdbm-demo",
from plone.directives import form
import os
from zExceptions import Forbidden
from suds.client import Client
from suds.plugin import MessagePlugin
import urllib2
import xml.etree.ElementTree as ET


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


 
    

ppo_vocab=SimpleVocabulary([
    SimpleTerm(value=u'b', title=(u'Bill')),
    SimpleTerm(value=u'a', title=(u'Bill')),
    ])

def coleccionesVocab(context):
    "colecciones en "
    cl=ClienteGS()
    terms = []  
    return SimpleVocabulary.fromValues(cl.dameListadoColecciones())

directlyProvides(coleccionesVocab, IContextSourceBinder)


class IEditGS(form.Schema):
    """Campos del formulario de edición de un documento Greenston3 en el import!"""    
    form.widget('coleccion', klass='recargaForm')
    
    coleccion= schema.Choice(
        title=u"Colección",
        description=u"Elija una colección para editar",
        source=coleccionesVocab,        
        required=True,
    )   
    obra = schema.Choice(
        title=u"Obra",
        description=u"Elija una obra para editar",        
        source=obrasVocab,
        required=False,
    )
    obraTmp= schema.TextLine(
        title=u"obraTmp",
        description=u"una pavada",
        required=False,
    )
    itemT= schema.TextLine(
        title=u"Item Título",
        description=u"no se que es... sera el título del documento",
        required=False,
    )    
    itemNat= schema.TextLine(
        title=u"Naturaleza del documento",
        description=u"y esto que es?",
        required=False,
    )
    itemEdi= schema.TextLine(
        title=u"Item edición",
        description=u" esto que es?",
        required=False,
    )
    form.widget('anotacion', klass='recargaForm',size=5)
    anotacion = schema.Text(title=u"Editar Metadato",required=False,)
    
class EditGS(form.SchemaForm):
    """ 
    Edita un documento de Greenstone3 desde el import!
    """
    grok.name('editGs')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = IEditGS
    ignoreContext = True

    label = u"Editando un Documento GS"
    description = u"Solo modificación de anotacion"
    fsmanager=""
    coleccion=""
    editOk=False
    
    @property
    def mmi_vocab(self):
        cl=ClienteGS()
        
        return SimpleVocabulary.fromValues(cl.getObras(self.coleccion))
        
    
    def updateWidgets(self):
        super(EditGS, self).updateWidgets()
        if len(self.widgets["coleccion"].value)>0:
            self.coleccion=self.widgets["coleccion"].value[0]            
        
        if self.showObras():
            self.widgets['obraTmp'].mode = INPUT_MODE            
            self.widgets['obra'].field.vocabulary = self.mmi_vocab
        else:
            self.widgets['obraTmp'].mode = HIDDEN_MODE
    
    def showObras(self):
        # Set a custom widget for a field for this form instance only          
        if self.widgets["obraTmp"].value!="":
            return True
        else:
            return False
        

    def showSave(self):
        if "form.buttons.editar" in self.request.form:
            return True
        else:
            return False
    
    @button.buttonAndHandler(u'Buscar identificador')
    def obrasHandler(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        pass
        
        
    @button.buttonAndHandler(u'Editar',condition=showObras)
    def editHandler(self, action):
        """
            [u'ae.itemtitulo',u'ae.itemedicion',u'ae.itemnaturaleza',u'pr.idpreservacion',u'ae.filetitulo',u'bi.anotacion1','ae.coleccionnombreautor',u'bi.ruta']
        """
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return

        infoMetadatos={"itemT":u"ae.itemtitulo","itemEdi":u"ae.itemedicion","itemNat":u"ae.itemnaturaleza","anotacion":u"bi.anotacion1"}
        
        #ruta del documento a editar
        cli=ClienteGS()
        ruta=cli.dameRutaXMLDeId(self.widgets["coleccion"].value[0], self.widgets["obraTmp"].value)
        
        if ruta=="":
            print self.widgets["obraTmp"].value
            self.status = 'Falta el metadato "bi.ruta"'
            return        
        
        # Do something with valid data here
        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)
        self.editOk=True
        self.fsmanager=FSManager()
        self.fsmanager.openF(self.widgets["coleccion"].value[0])
        for v in infoMetadatos:
            metaValue=self.fsmanager.dameMetadata(infoMetadatos[v])
            self.widgets[v].value=metaValue
        self.status = "Articulo encontrado"

    @button.buttonAndHandler(u'Guardar',condition=showObras)
    def saveHandler(self, action):  
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        dicDatos={
            "version":"1",
            "idColec":self.widgets["coleccion"].value[0],
            "metadatos":[("bi.anotacion1",self.widgets["anotacion"].value),
                         ("ae.itemtitulo",self.widgets["itemT"].value),
                         ("ae.itemedicion",self.widgets["itemEdi"].value),
                         ("ae.itemnaturaleza",self.widgets["itemNat"].value),
                         ]}
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

    
































import xml.etree.ElementTree as ET

class FSManager:
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'
    miXml=""
    
    def openF(self,colecName):
        self.openFile(self.xmlFileBase+colecName+self.xmlFileResto+self.xmlFileName)
        
    def openFile(self, ruta):
        try:
            xmlFile = ET.parse(ruta)
            self.miXml=xmlFile
            print "ok"
        except e:        
            print e            


    def dameSigVerison(self,carpeta):        
        listado=os.listdir(carpeta)
        tmp=["1"]
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
        pathFolder=self.xmlFileBase+obModificado["idColec"]+self.xmlFileResto        
        version=self.dameSigVerison(pathFolder)        

        newfilename=self.xmlFileBase+obModificado["idColec"]+self.xmlFileResto+"metadataV"+version+".xml"

        self.openF(obModificado["idColec"])

        for met in obModificado["metadatos"]:
            try:             
                self.miXml.findall('.//Metadata[@name="'+met[0]+'"]')[0].text=met[1]
                
            except:
                print "no pude guardar el metadato %s > %s" %(met[0],met[1])  
        try:
            self.miXml.write(newfilename,encoding="UTF-8", xml_declaration=True)
        except:
            print "problema guardando el archivo"
            return False
        return True
        
    def dameMetadata(self,strMeta):
        try:
            root = self.miXml.getroot()
        except e:
            print "no se puede parsear el xml"
            return []
        
        meta=self.miXml.findall(u'.//Metadata[@name="'+strMeta+'"]')[0].text
        metadato=meta
        return metadato





class ClienteGS:
    ###ruta = "%s%s%s"%(self.xmlFileBase,self.coleccion,self.xmlFileResto)###
    coleccion  ="puig"
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
        
    def todasObrasDeColeccion(self,coleccion):
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
            query =client.service.browseDescendants(self.coleccion,"",self.idioma,infoClasi)
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
    
    def getObras(self,colecName):
        """devuelve una lista para armar el select"""
        print colecName
        
        obras=self.todasObrasDeColeccion(colecName)
        pasadas=[]
        ls=[]
        
        for elem in obras:   
            if elem["ae.filetitulo"] not in pasadas:
                ls.append({"value":elem["id"],"title":elem["ae.filetitulo"]})
                pasadas.append(elem["ae.filetitulo"])
        return ls
    
    def getObrasList(self,colecName):
        obras=self.getObras(colecName)
        res=[]
        for r in obras:
            
        
        
    
    
    
    def buscaEnColeccion(self,coleccion="puig"):
        ###Devuelve los metadatos de las obras encontradas###        
        pass
    
    def defDameObrasEmpaquetadas(self):
        ###Devuelve los metadatos de cada obra###    
        pass
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

     

        
    