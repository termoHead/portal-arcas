 # -*- coding: utf-8 -*-
__author__ = 'Paul'
#"lucene-jdbm-demo",

import os
import sys
from zExceptions import Forbidden
from suds.client import Client
from suds.plugin import MessagePlugin
import urllib2
import xml.etree.ElementTree as ET
from plone.autoform import directives
from arcas.content.rootFolder import IRootFolder
from Products.CMFPlone.utils import safe_unicode

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

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFCore.utils import getToolByName
    
COLECCION=""
SERIE=""
SUBSERIE=""

def serie_vocab(self):
    global COLECCION
    print ">>>"+COLECCION
    if COLECCION=="":
        return  SimpleVocabulary([])
    terms=[]
    cl=ClienteGS()
    lista=cl.getSeries(COLECCION)
    for pair in lista:
        if pair["value"]!=False or  pair["value"]!=True or   pair["value"]!="true" or  pair["value"]!="false": 
            terms.append(SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]))
    return SimpleVocabulary(terms)

def subserie_vocab(self):
    global SERIE
    global COLECCION        
    
    if COLECCION!="" and SERIE!="":
        cl=ClienteGS()        
        tieneSub=cl.tieneSubSerie(COLECCION)
        terms=[]
        if tieneSub:
            lista=cl.getDocsFromSerie(COLECCION,SERIE)            
            for pair in lista:   
                if pair["value"]!=False or pair["value"]!=True or   pair["value"]!="true" or  pair["value"]!="false":
                    terms.append(SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]))
            return SimpleVocabulary(terms)
   
    return  SimpleVocabulary([])
    
def item_vocab(self):
    global SERIE
    global SUBSERIE
    global COLECCION        
    if COLECCION!="" and SUBSERIE!="":    
        cl=ClienteGS()        
        tieneSub=cl.tieneSubSerie(COLECCION)
        terms=[]
        if tieneSub:
            lista=cl.getDocsFromSubSerie(COLECCION,SUBSERIE)            
            for pair in lista:                
                terms.append(SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]))
            return SimpleVocabulary(terms)
        else:            
            lista=cl.getDocsFromSerie(COLECCION,SERIE)
            for pair in lista:                
                terms.append(SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]))
            return SimpleVocabulary(terms)
    return  SimpleVocabulary([])

iso_idiomas=SimpleVocabulary([
    SimpleTerm(value=u'ay', title=(u'aimara')),
    SimpleTerm(value=u'de', title=(u'alemán')),
    SimpleTerm(value=u'es', title=(u'español (o castellano)')),
    SimpleTerm(value=u'fr', title=(u'francés')),
    SimpleTerm(value=u'el', title=(u'griego (moderno)')),
    SimpleTerm(value=u'gn', title=(u'guaraní')),
    SimpleTerm(value=u'en', title=(u'inglés')),
    SimpleTerm(value=u'it', title=(u'italiano')),
    SimpleTerm(value=u'la', title=(u'latín')),
    SimpleTerm(value=u'pt', title=(u'portugués')),
    SimpleTerm(value=u'qu', title=(u'quechua'))
    ])

def coleccionesVocab(context):
    "colecciones en "
    cl=ClienteGS()
    mt=getToolByName(context,"portal_membership")
    catalogo=getToolByName(context,"portal_catalog")
    idColec = mt.getAuthenticatedMember().getProperty('participaEn',None)
    colectL=[]
    for elem in idColec.split(","):        
        colec=catalogo(id=elem)[0]
        colectL.append(colec.getObject().GS_ID)
        
    
    lista=cl.dameListadoColecciones()
    
    terms = [lista[0]]    
    for idGs in colectL:
        if idGs in lista:    
            terms.append(idGs)            
    if len(terms)>1:
        return SimpleVocabulary.fromValues(terms)
    else:
        return SimpleVocabulary.fromValues(lista)

directlyProvides(coleccionesVocab, IContextSourceBinder)
directlyProvides(serie_vocab, IContextSourceBinder)
directlyProvides(subserie_vocab, IContextSourceBinder)
directlyProvides(item_vocab, IContextSourceBinder)



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
    f_idioma= schema.Choice(
        title=u"Idioma",
        vocabulary=iso_idiomas,
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
    f_anotacion = schema.Text(title=u"Anotación",required=False,)
    
class IGsSubSerie(form.Schema):
    model.fieldset('Subserie',
        label=(u"Metadatos de la Sub Serie"),
        fields=["sub_titulo","sub_alcance","sub_anotacion",]
    )
    sub_titulo= schema.TextLine(
        title=u"Título",
        description=u"titulo de la sub serie",
        required=False,
    )  
    sub_alcance= schema.TextLine(
        title=u"Alcance",
        description=u"Alcance de la subserie",
        required=False,
    ) 
    sub_anotacion=schema.TextLine(
        title=u"Anotación",        
        required=False,
    ) 
    
class IGsMetaSerie(form.Schema):
    model.fieldset('Item',label=(u"Metadatos de la serie"),
        fields=["s_titulo","s_temporal","s_autor","s_extension","s_caracteristicas","s_alcance","s_lenguaiso"]
    )
    s_titulo= schema.TextLine(title=u"Titulo",
        description=u"no se que es... sera el título del documento",required=False,) 
    s_temporal= schema.TextLine(title=u"Extensión Temporal",
        description=u"no se que es... sera el título del documento",required=False,) 
    s_autor= schema.TextLine(title=u"Autor",
        description=u"no se que es... sera el título del documento",required=False,) 
    s_extension= schema.TextLine(title=u"Extensión",
        description=u"no se que es... sera el título del documento",required=False,)
   
    s_caracteristicas= schema.TextLine(title=u"Caracteristicas",
        description=u"no se que es... sera el título del documento",required=False,)
    s_alcance= schema.TextLine(title=u"Alcance",
        description=u"no se que es... sera el título del documento",required=False,)
    s_lenguaiso = schema.Choice(
        title=u"Idioma",
        vocabulary=iso_idiomas,
        required=False,
    )

class IEditGS(form.Schema, IGsMetaSerie , IGsSubSerie,IGsMetaItem ):
    """Campos del formulario de edición de un documento Greenston3 en el import!"""    
    model.fieldset('Datos',
        label=(u"Datos de la Obra"),
        fields=["coleccion","serie","subserie","obra","obraTmp"]
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
        source=serie_vocab,
        required=False,
    )
    subserie= schema.Choice(
        title=u"Sub Serie",
        description=u"Elija una sub serie para editar",        
        source=subserie_vocab,
        required=False,
    )
    obra = schema.Choice(
        title=u"Obra",
        description=u"Elija una obra para editar",        
        source=item_vocab,
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
    grok.require('zope2.View')
    #grok.require('cmf.ListFolderContents')
    #grok.require('arcas.addExhibicion')
    grok.context(IRootFolder)
    schema = IEditGS
    ignoreContext = True    
    label       = u"Editando un Documento GS"
    description = u"Edición de metadatos"
    fsmanager   = ""
    coleccion   = "cordemia"
    serie       = ""
    obra        = ""
    saveFlag    = 0
    msjForm     = ""
    
    lsw=["f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones","f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta"]

    infoMetadatosSerie={'s_titulo':'ae.serietitulo','s_temporal':'ae.seriecoberturatemporal','s_extension':'ae.fileextension','s_caracteristicas':'ae.seriedescripcionfisica','s_autor':'ae.serieautor','s_alcance':'ae.seriealcance','s_lenguaiso':'ae.serielenguaiso'}

    infoMetadatoSubSerie={'sub_titulo':'ae.subserietitulo','sub_alcance' :'ae.subserieautor','sub_anotacion':'ae.subserielenguaiso'}

    infoMetaItem={ 'f_fechaCreacion':'ae.itemcoberturatemporal','f_lugarCreacion':'bi.lugar','f_descFisica':'ae.itemdescripcionfisica','f_dimensiones':'ae.itemdimension','f_idioma':'ae.itemlenguaiso','f_naturaleza':'ae.itemnaturaleza','f_alcance':'ae.itemalcance','f_anotacion':'bi.anotacionitem','f_ruta':'bi.ruta'}
    
    editOk=False
    
    def update(self):
        global COLECCION
        global SERIE
        global SUBSERIE        
        super(EditGS, self).update()
        """
        tmpG=[]
        ordenGrupos=[u"Metadatos del Item",u"Metadatos de la Sub Serie", u"Metadatos de la serie"]
        for grupo in ordenGrupos:
            for elem in self.groups:
                if elem.label==grupo:
                    tmpG.append(elem)
        
        tmpG.append(self.groups[3])
        self.groups=tuple(tmpG)
        """
        
        COLECCION=SERIE=SUBSERIE=""
        colec = self.request.get('coleccion', None)

        if(len(self.groups[3].widgets["coleccion"].value)>0):
                COLECCION=self.groups[3].widgets["coleccion"].value[0]
        if colec:
            self.groups[3].widgets["coleccion"].value = colec.encode('utf-8')
            COLECCION=self.groups[3].widgets["coleccion"].value

        if(len(self.groups[3].widgets["serie"].value)>0):
            if self.groups[3].widgets["serie"].value[0] != "--NOVALUE--":
                SERIE=self.groups[3].widgets["serie"].value[0]

        if(len(self.groups[3].widgets["subserie"].value)>0):
            if self.groups[3].widgets["subserie"].value[0] != "--NOVALUE--":
                SUBSERIE=self.groups[3].widgets["subserie"].value[0]
        super(EditGS, self).update()
        
        if colec:
            self.groups[3].widgets["coleccion"].value = colec.encode('utf-8')
            COLECCION=self.groups[3].widgets["coleccion"].value
            self.groups[3].widgets["coleccion"].mode = HIDDEN_MODE
    
    def showObras(self):
        # Set a custom widget for a field for this form instance only       
        if self.groups[0].widgets["f_ruta"].value!=u"":
            return True
        else:
            return False

    def showSave(self):
        if "form.buttons.editar" in self.request.form:
            return True
        else:
            return False

    @button.buttonAndHandler(u'Guardar',condition=showObras)
    def saveHandler(self, action):
        self.saveFlag=self.saveFlag+1
   
        if self.saveFlag<2:
            msj=rutaItem=rutaSubSerie=rutaSerie=""
            subSerieOk=False

            infoMetadatos=self.infoMetaItem
            infoMetadatosSerie=self.infoMetadatosSerie

            data, errors = self.extractData()

            if len(self.groups[3].widgets["subserie"].value)>0:
                subSerieOk=True
                infoMetadatoSubSerie=self.infoMetadatoSubSerie

            if errors:
                self.status = self.formErrorsMessage
                return
                
            #rutaArchivos
            rutaItem= self.groups[0].widgets["f_ruta"].value        
            
            if subSerieOk:            
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

            
            
            #-------- cargo ITEM
            tmpList=[]
            for x in infoMetadatos:
                itFtext=self.groups[0].widgets[x].value
                if type(itFtext)==type([]):
                    itFtext=itFtext[0]                
                tmpList.append((EditGS.infoMetaItem[x],itFtext))
                
            dicDatosItem={
                "version":"1",
                "idColec":self.groups[3].widgets["coleccion"].value[0],
                "ruta":rutaItem,
                "folder":self.groups[3].widgets["coleccion"].value[0]+"/"+rutaItem.replace("/metadata.xml",""),
                "metadatos":tmpList,
                #"metadatos":[(EditGS.infoMetaItem[x],self.groups[2].widgets[x].value) for x in infoMetadatos]
                }
                
            #-------- cargo ITEM    
            tmpList=[]
            for x in infoMetadatosSerie:
                itFtext=self.groups[2].widgets[x].value
                if type(itFtext)==type([]):
                    itFtext=itFtext[0]                
                tmpList.append((EditGS.infoMetadatosSerie[x],itFtext))
            
            dicDatosSerie={
                "version":"1",
                "idColec":self.groups[3].widgets["coleccion"].value[0],
                "ruta":rutaSerie,
                "folder":self.groups[3].widgets["coleccion"].value[0]+"/"+rutaSerie.replace("/metadata.xml",""),
                "metadatos":tmpList,
                #"metadatos":[(EditGS.infoMetadatosSerie[x],self.groups[0].widgets[x].value) for x in infoMetadatosSerie]
            }
            
            if subSerieOk:
                tmpList=[]
                for x in infoMetadatoSubSerie:
                    itFtext=self.groups[1].widgets[x].value
                    if type(itFtext)==type([]):
                        itFtext=itFtext[0]                
                    tmpList.append((EditGS.infoMetadatoSubSerie[x],itFtext))
                    
                dicDatosSubSerie={
                    "version":"1",
                    "idColec":self.groups[3].widgets["coleccion"].value[0],
                    "ruta":rutaSubSerie,
                    "folder":self.groups[3].widgets["coleccion"].value[0]+"/"+rutaSubSerie.replace("/metadata.xml",""),
                    "metadatos":tmpList
                }
             
            
            self.fsmanager=FSManager()
            flagm=0
            
            
            itemsaved=self.fsmanager.saveFile(dicDatosItem)
            seriesaved=self.fsmanager.saveFile(dicDatosSerie)
 
            if itemsaved[0]=="error":
                msj="> No se pudo guardar el item en %s"%rutaItem
                flagm+=1

            if seriesaved[0]=="error":
                msj="> No se pudo guardar la serie en %s"%rutaSerie                             
                flagm+=1                
            
                    
            if subSerieOk:            
                subSeriesaved=self.fsmanager.saveFile(dicDatosSubSerie)
                if subSeriesaved[0]=="error":
                    msj="> No se pudo guardar la sub serie en %s" %rutaSubSerie                    
                    flagm+=1
            else:
                subSeriesaved='sin sub serie'
            
            if flagm==0:
                mandoCorreo=self.emails({'ritem':itemsaved,'rsubserie':subSeriesaved,'rserie':seriesaved})
                if mandoCorreo:
                    self.msjForm =u"Los cambios fueron guardados. Se generó una nueva versión de metadatos y se envió un para control"
                else:
                    self.msjForm =u"Los cambios fueron guardados. Pero hubo un error al querer enviar el correo."
            else:
                self.msjForm =u"No se pudieron guardar los cambios... se ha generando reporte"
        else:
            self.status=self.msjForm


    @button.buttonAndHandler(u"Cancel",condition=showObras)
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""
        global COLECCION
        global SERIE
        global SUBSERIE

        COLECCION=SERIE=SUBSERIE=""        
        self.status = "Cambios cancelados"
        self.editOk = False
        self.form._finishedAdd = True
        miurl=self.context.REQUEST.URL
        self.context.REQUEST.RESPONSE.redirect(miurl)



    def emails(self,datos):        
        sender="admin@arcas.unlp.edu.ar"
        mt=getToolByName(self.context,"portal_membership")

        operarioMail    = mt.getAuthenticatedMember().getProperty('email',None)
        operarioNombre  = mt.getAuthenticatedMember().getProperty('fullname',None)

        if operarioMail=='':
            operarioMail="pablomusa@gmail.com"

        if operarioNombre=='':
            operarioNombre="Pablo Musa"

        coordinadorMail = "pablomusa@gmail.com"
        reciver=[operarioMail,coordinadorMail]

        rutasItem =  datos["ritem"]
        rutasSerie =  datos["rserie"]
        rutasSubSerie =  datos["rsubserie"]

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[ARCAS] Cambios en los metadatos de un registro"
        msg['From'] = sender
        msg['To'] = reciver[0]+','+reciver[1]

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hola!\nSe modificaron metadatos en el Greenston de ARCAS.\n Los Archivos son: %s\n %s \n%s" %(rutasSerie,rutasSubSerie,rutasItem)

        hhtml = u"<html><head></head><body><h2>Hola</h2>"
        hhtml += u"El usuario: %s, realizó modificaciones en los matadatos de ARCAS.</br>" %operarioNombre.decode("utf8")
        hhtml += u"<p>Esto es un registro básico de lo realizado:</p><ul>"
        hhtml += u"<li><b>Serie:</b><ul>"

        for stra in rutasSerie:
            hhtml += '<li>'+stra.decode('utf8')+'</li>'
        if len(rutasSerie)==1:
            hhtml += '<li>Sin cambios</li>'

        hhtml += "</ul></li>"

        hhtml += u"<li><b>SubSerie:</b><ul>"   
        for stra in rutasSubSerie:
            hhtml += '<li>'+stra.decode('utf8')+'</li>'            
        if len(rutasSubSerie)==1:
            hhtml += '<li>Sin cambios</li>'
        hhtml += "</ul></li>"

        hhtml += u"<li><b>Item:</b><ul>"
        for stra in rutasItem:
            hhtml += '<li>'+stra.decode('utf8')+'</li>'
        if len(rutasItem)==1:
            hhtml += '<li>Sin cambios</li>'            
        hhtml += "</ul></li>"

        hhtml += u"</ul><hr/><p>Este es un mail automático, por favor no responder. En caso de errores "
        hhtml += u"comunicarse con mariana@fahce.unlp.edu.ar</p>Gracias.</p>"
        hhtml += u"</br></br><p></p>"
        hhtml += u"</body></html>"
        # Record the MIME types of both parts - text/plain and text/html.        
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(hhtml.encode('utf8'), 'html')
        msg.attach(part1)
        msg.attach(part2)
        try:
            s = smtplib.SMTP('localhost')
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            s.sendmail(sender, reciver, msg.as_string())      
            s.quit()
            return True
        except Exception:
            print "Error: unable to send email"
            return False

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
        rut=self.xmlFileBase+carpeta
        listado =os.listdir(rut)
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
            
        if len(listR)==1:
            if len(listR[0])==0:
                return "1"
                
            
        
        listR.sort()
        nex=listR[-1]
        resultado = str(int(nex[1:])+1)
        return resultado
        
    def creatNewXmlMetadata(self,name,dato):
        nodo=ET.Element('Metadata',{'mode':'accumulate','name':name})
        nodo.text=dato
        return nodo
    
    def saveFile(self,obModificado):
        """
            guarda los datos en el xml
        """
        listlog=[]
        logstr=""
        pathFolder      =obModificado["idColec"]+"/"+obModificado["ruta"]
        pathFolder      =obModificado["folder"]
        version         =self.dameSigVerison(pathFolder)        
        #newfilename     =obModificado["ruta"].replace("metadata.xml",self.xmlFileResto+"metadataV"+version+".xml")
        newfilename     =obModificado["ruta"].replace("metadata.xml","metadataV"+version+".xml")
        newfilename     =self.xmlFileBase+obModificado["idColec"]+"/"+newfilename
        rm              =self.openF(obModificado["ruta"],obModificado["idColec"])

        if rm == False:
            return False
        
        #elemino todos los metadatos del xml cargado
        docTypeHeader='<?xml version=\"1.0\" encoding=\"UTF-8\"?><!DOCTYPE DirectoryMetadata SYSTEM \"http://greenstone.org/dtd/DirectoryMetadata/1.0/DirectoryMetadata.dtd \">'
        copiXml=self.miXml.getroot()
        
        
        #actualizo los que estan
        for itemXml  in copiXml.find(".//FileSet/Description").findall(".//Metadata"):
            itXnom=itemXml.attrib["name"]
            itXtext=itemXml.text
            
            for itemForm in obModificado["metadatos"]:
                itFnom =  itemForm[0]
                itFtext=  itemForm[1]

                if itFnom==itXnom:
                    if itFtext=="":
                        #Si en el formulario el metadato está vacio lo borro el XNL                        
                        copiXml.find(".//FileSet/Description").remove(itemXml)               
                        #logstr="%s quedó vacio y se eliminó del metadata.xml" %itFnom
                        #listlog.append(logstr)
                    else:
                        #actualizo el dato en el XNL con el valor que viene del form
                        #puede venir una lista por los idiomas o un str 
                        if type(itFtext)==type([]):
                            if itXtext!=itFtext[0]:
                                itemXml.text=itFtext[0]
                                logstr="actualizado> %s: %s" %(itFnom,itFtext[0])
                                listlog.append(logstr)
                        else:
                            itemXml.text=itFtext
                            if itXtext!=itFtext:
                                itemXml.text=itFtext
                                logstr="actualizado> %s: %s" %(itFnom,itFtext)
                                listlog.append(logstr)
                        flagMatch=True
                    break
                
                
        ##agrego el elemento nuevo que no estaban en el FS XML mingshaobi     
        for itemForm in obModificado["metadatos"]:
            itFnom =  itemForm[0]
            itFtext=  itemForm[1]
            
            if type(itFtext)==type([]):
                itFtext=itFtext[0]

            flagMatch=False
            
            for itemXml  in copiXml.find(".//FileSet/Description").findall(".//Metadata"):
                itXnom=itemXml.attrib["name"]
                if itXnom == itFnom:
                    flagMatch=True
                    break

            if flagMatch==False:

                if itFtext!="":
                    no=self.creatNewXmlMetadata(itFnom,itFtext)
                    copiXml.find(".//FileSet/Description").append(no)
                    logstr="nuevo> %s: %s." %(itFnom,itFtext)
                    listlog.append(logstr)
        
        xmlstr=ET.tostring(copiXml)
        
        try:
            f=open(newfilename,"wr+")
            newstr=docTypeHeader+xmlstr           
            f.write(newstr)
            f.close()
            logstr=newfilename
            listlog.insert(0,logstr)
            
        except:
            e = sys.exc_info()[0]
            print "Problema: %s"% e
            logstr=newfilename
            listlog.insert(0,"error")
            
        return listlog
        
        
    def dameMetadata(self,strMeta):
        try:
            root = self.miXml.getroot()
        except:
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
        
  
        
        import pdb
        pdb.set_trace()
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