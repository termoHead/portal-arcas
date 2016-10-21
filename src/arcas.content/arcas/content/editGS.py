# -*- coding: utf-8 -*-
__author__ = 'Paul'
#"lucene-jdbm-demo",
from plone.directives import form

from zExceptions import Forbidden
from suds.client import Client
from suds.plugin import MessagePlugin
import urllib2
import xml.etree.ElementTree as ET



"""

    Simple sample form

"""
from five import grok
from plone.directives import form

from zope import schema
from z3c.form import button
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import action
from zope.component import getMultiAdapter


coleccionesVocab = SimpleVocabulary(
    [SimpleTerm(value=u'cordemia', title=u'CorDeMiA'),
     SimpleTerm(value=u'puig', title=u'M. Puig'),
     SimpleTerm(value=u'vigo', title=u'E. Vigo')
     ]
    )
puig_obrasVocab = SimpleVocabulary(
    [SimpleTerm(value=u'puigNBpDesc0001', title=u'Boquitas pintadas'),
     SimpleTerm(value=u'puigNCntDesc0001', title=u'Cae la noche tropical'),
     SimpleTerm(value=u'puigNBmaDesc0001', title=u'El beso de la mujer araña'),
     SimpleTerm(value=u'puigNTrhDesc0001', title=u'La traición de Rita Hayworth'),
     SimpleTerm(value=u'puigNMeqlepDesc0001', title=u'Maldición eterna a quien lea estas páginas')
     ]
    )    
vigo_obrasVocab = SimpleVocabulary(
    [SimpleTerm(value=u'puigNBpDesc0001', title=u'Vigo_Bopintadas'),
     SimpleTerm(value=u'puigNCntDesc0001', title=u'Vigo_Ca'),
     SimpleTerm(value=u'puigNBmaDesc0001', title=u'Vigo_El mujer araña'),
     SimpleTerm(value=u'puigNTrhDesc0001', title=u'Vigo_Rita Hayworth'),
     SimpleTerm(value=u'puigNMeqlepDesc0001', title=u'Vigo_Maldáginas')
     ]
    )    
cordemia_obrasVocab = SimpleVocabulary(
    [SimpleTerm(value=u'puigNBpDesc0001', title=u'cordemia 1'),
     SimpleTerm(value=u'puigNCntDesc0001', title=u'coordemia tropical'),
     SimpleTerm(value=u'puigNBmaDesc0001', title=u'coordemia  araña'),
     SimpleTerm(value=u'puigNTrhDesc0001', title=u'24524525424'),
     SimpleTerm(value=u'puigNMeqlepDesc0001', title=u'cordemia  a quien lea estas páginas')
     ]
    )

class IEditGS(form.Schema):
    """ Define form fields """
    
    coleccion= schema.Choice(
        title=u"Colección",
        description=u"Elija una colección para editar",
        vocabulary=coleccionesVocab,
        required=True,
    )
    
    obra = schema.Choice(
        title=u"Obra",
        description=u"Elija una obra para editar",        
        vocabulary=cordemia_obrasVocab,
        required=False,
    )
    anotacion = schema.Text(
        title=u"Editar Metadato",        
        required=False,
    )

        
class EditGS(form.SchemaForm):
    """ Define Form handling

    This form can be accessed as http://yoursite/@@my-form

    """
    grok.name('editGs')
    grok.require('zope2.View')
    grok.context(ISiteRoot)

    schema = IEditGS
    ignoreContext = True

    label = u"Editando un Documento GS"
    description = u"Solo modificación de anotacion"
    fsmanager=""
    editOk=False
    def update(self):
        super(EditGS, self).update() 
        
        
    def actulizaObras(self):
        # Set a custom widget for a field for this form instance only        
        if len(self.widgets["obra"].value)>0:
            if self.widgets["coleccion"].value[0]== u"vigo":
                self.widgets["obra"].field.vocabulary=vigo_obrasVocab
            elif self.widgets["coleccion"].value[0]== u"cordemia":
                self.widgets["obra"].field.vocabulary=cordemia_obrasVocab
            elif self.widgets["coleccion"].value[0]== u"puig":
                self.widgets["obra"].field.vocabulary=puig_obrasVocab

    def updateWidgets(self):
        super(EditGS, self).updateWidgets()
        self.actulizaObras()
    
    def showEdit(self):
        if len(self.widgets["obra"].value)>0:
            self.editOk=True
            return True           
        else:
            self.editOk=False
            return False
        
    def showSave(self):
        if self.widgets["anotacion"].value!="":
            return True
        else:
            return False
    
    
    @button.buttonAndHandler(u'Actulizar')
    def actualizarHandler(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
            
    @button.buttonAndHandler(u'Guardar',condition=showSave)
    def saveHandler(self, action):        
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return        
        dicDatos={
            "version":"1",
            "idColec":self.widgets["coleccion"].value[0],
            "metadatos":[("bi.anotacion1",self.widgets["anotacion"].value),]
            }
        self.fsmanager=FSManager()
        if self.fsmanager.saveFile(dicDatos):
            self.status =u"Cambios guardados... mail to M. Pichinini!"
        else:
            self.status =u"No se pueden guardar los cambios... generando reporte"

            
    @button.buttonAndHandler(u'Editar',condition=showEdit)
    def editHandler(self, action):
        data, errors = self.extractData()
        
        if errors:
            self.status = self.formErrorsMessage
            return

        # Do something with valid data here

        # Set status on this form page
        # (this status message is not bind to the session and does not go thru redirects)
        self.editOk=True
        self.fsmanager=FSManager()
        self.fsmanager.openF(self.widgets["coleccion"].value[0])
        metaValue=self.fsmanager.dameMetadata('bi.anotacion1')        
        self.widgets["anotacion"].value=metaValue
        self.status = "Articulo encontrado"
        

    @button.buttonAndHandler(u"Cancel", condition=showSave)
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
        
    def saveFile(self,obModificado):
        """guarda los datos en el xml"""        
        newfilename=self.xmlFileBase+obModificado["idColec"]+self.xmlFileResto+"metadataV"+obModificado["version"]+".xml"
        self.openF(obModificado["idColec"])
        
        for met in obModificado["metadatos"]:
            try:                
                self.miXml.findall('//Metadata[@name="'+met[0]+'"]')[0].text=met[1]
            except:
                import pdb
                pdb.set_trace()
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
        
        metadato=self.miXml.findall('//Metadata[@name="'+strMeta+'"]')[0].text.encode("utf8")
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
        result=[]
        for e in query.findall('coletionList//collection'):
            result.append(e.text)            
        return result
        
    def todasObrasDeColeccion(self,coleccion="puig"):
        ###Dada una coleccion devuelve una listado de ids de documentos###    
        client=self.client
        listado=[]
        docsId              =client.factory.create("ArrayOf_xsd_string") 
        infoMetadatos       =client.factory.create("ArrayOf_xsd_string") 
        infoClasi           =client.factory.create("ArrayOf_xsd_string") 
        infoClasi.value     =[u"CL1"]
        infoMetadatos.value =[u"pr.idpreservacion",u"ae.filetitulo",u"bi.anotacion1",u"Source"]
        
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
        
        
        
        for item in xmlTmp.getiterator():
            if item.tag=="documentNode":
                itemML=item.getchildren()[0]
                itemMD=itemML.getchildren()[0]
                itemMDTitu=itemML.getchildren()[1]
                try:
                    itemMDTexto=itemML.getchildren()[2]
                except:
                    itemMDTexto="st"
                
                if itemMD.tag=="metadata":
                    resp.append({
                        'hash':item.get("nodeID"),
                        'preserva':itemMD.text,
                        'titulo':itemMDTitu.text,
                        'texto':safe_unicode(dato)
                    })
        return resp 
    
        
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

     

        
    