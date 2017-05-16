# -*- coding: utf-8 -*-
__author__ = 'Paul'
import os
from arcas.content.coleccion import IColeccion
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
from plone.supermodel import model

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFCore.utils import getToolByName

from arcas.content.editGS import IGsMetaItem,IGsSubSerie,IGsMetaSerie,iso_idiomas,serie_vocab,coleccionesVocab,item_vocab,subserie_vocab

from arcas.content.FSManager import FSManager
from plone.namedfile.field import NamedFile
from z3c.form import field, group
from arcas.content.config import infoMetaItem,infoMetadatoSubSerie,infoMetadatosSerie
from arcas.content.config import MAIL_ADMIN , MAIL_COORDINADOR

   
class IEditItem(form.Schema, IGsMetaSerie , IGsSubSerie,IGsMetaItem ):
    """Campos del formulario de edición de un documento Greenston3 en el 
import!   """ 
    model.fieldset('Selección de ítem Serie ',
        label=(u"Elija una serie para editar"),
        fields=["coleccion","serie","subserie","obra","obraTmp","tituColec"]
        
    )    
    
    
    form.widget('coleccion', klass='recargaForm')
    directives.mode(coleccion='hidden')
    coleccion= schema.TextLine(
        title=u"Colección",        
        required=True,
    )

    directives.mode(serie='hidden')
    serie = schema.TextLine(
        title=u"Serie",
        required=False,
    )
    directives.mode(subserie='hidden')
    subserie= schema.TextLine(
        title=u"Sub Serie",
        description=u"Elija una sub serie para editar",
        required=False,
    )
    directives.mode(obra='hidden')
    obra = schema.TextLine(
        title=u"Obra",
        required=False,
    )

    directives.mode(obraTmp='hidden')
    obraTmp= schema.TextLine(
        title=u"obraTmp",
        description=u"una pavada",
        required=False,
    )

    directives.mode(tituColec='hidden')
    tituColec= schema.TextLine(
        title=u"Título",
        description=u"título de la colección que está siendo editada",
        required=False,
    )

class EditItem(form.SchemaForm):
    """
       Edita un documento de Greenstone3 desde el import!
    """
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'
    
    grok.name('editItem')
    grok.require('zope2.View')
    #grok.require('cmf.ListFolderContents')
    #grok.require('arcas.addExhibicion')
    grok.context(IRootFolder)
    schema = IEditItem
    
    ignoreContext = True    
    label       = u"Formulario para edición de datos descriptivos de las fuentes primarias"
    description = u'<div class="formuDescri">Los datos que usted va a editar se actualizarán una vez hayan sido revisados y aceptados\
                    para su inclusión/modificación por el equipo técnico de ARCAS. Recibirá un mail con la modificación \
                    por Usted realizada y cuando haya sido actualizado en el Portal público.<br \/>\
                    En todos los casos, el formulario mostrará para editar la versión pública. Si necesita modificar \
                    una versión generada por usted aún no publicada, utilice la información recibida por mail para \
                    recuperar los datos de las versiones intermedias.</div>\
                    '
    fsmanager   = ""
    coleccion   = "cordemia"
    serie       = ""
    obra        = ""
    saveFlag    = 0
    msjForm     = ""
    
    
    #lsw=["f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones","f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta"]

   
    editOk=False
    
    def update(self):
        global COLECCION
        global SERIE
        global SUBSERIE        
        super(EditItem, self).update()
        
        
        
        dictForm= self.request.form
        if 'cancel' in dictForm.keys():
            self.status="Los cambios fueron cancelados"
            return
        if 'formOk' in dictForm.keys():
            self.status=dictForm['formOk']
            return 
            
            
        if 'obra' in dictForm.keys():
            tituloC=self.dameTituloDeColeccionPorID_GS(dictForm["coleccion"])
            self.label=u'Editando la obra %s, de la colección: %s' %(dictForm["obra"],tituloC)
            
        COLECCION=SERIE=SUBSERIE=""        

        if "biruta" in dictForm:
            biruta=dictForm["biruta"]
            print biruta
            self.groups[0].widgets["f_ruta"].value=biruta
        else:
            #biruta=dictForm["form.widgets.f_ruta"]
            biruta=None

        if not biruta:
            return
        if "colec" in dictForm:
            colecId=dictForm["colec"]
        else:
            colecId=None
            
        if "coleccion" in dictForm:
            COLECCION=dictForm["coleccion"]
            self.groups[3].widgets["coleccion"].value=COLECCION
            self.groups[3].widgets["coleccion"].update()
            self.groups[3].widgets["obra"].value=dictForm["obra"]
            self.groups[3].widgets["obra"].update()
        else:
            COLECCION=None

        if "serie" in dictForm:
            SERIE=dictForm["serie"]
            self.groups[3].widgets["serie"].value=SERIE
            self.groups[3].widgets["serie"].update()
            #self.groups[3].widgets["serie"].value=SERIE
        else:
            SERIE=None

        if "subserie" in dictForm:
            SUBSERIE=dictForm["subserie"]
            self.groups[3].widgets["subserie"].value=SUBSERIE
            self.groups[3].widgets["subserie"].update() 
            #self.groups[3].widgets["subserie"].value=SUBSERIE
        else:
            SUBSERIE=None

        rutaItem = biruta
   
        
            
        
        #averigua si tiene subserie 
        if len(biruta.split("/")[3:])>4:
            subSerieOk=True
        else:
             subSerieOk=Flase
             
        
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
            
        fsmanager=FSManager()
        
        itemLoaded=fsmanager.parseXmlFileMetadata(COLECCION,biruta)
        
        
        itemSerieLoaded=fsmanager.parseXmlFileMetadata(COLECCION,rutaSerie)
        if subSerieOk:
            itemSubSerieLoaded=fsmanager.parseXmlFileMetadata(COLECCION,rutaSubSerie)
        
        for tupla in itemLoaded.items():
            try:
                widgetNumber=infoMetaItem.values().index(tupla[0])                  
                self.groups[0].widgets[infoMetaItem.keys()[widgetNumber]].value=tupla[1]
                self.groups[0].widgets[infoMetaItem.keys()[widgetNumber]].update()
            except:
                pass
                #print u"el elemento no está"

        for tupla in itemSerieLoaded.items():
            try:
                widgetNumber=infoMetadatosSerie.values().index(tupla[0])     
                self.groups[2].widgets[infoMetadatosSerie.keys()[widgetNumber]].value=tupla[1]
            except:
                pass
                #print u"el elemento no está"

        if subSerieOk:
            for tupla in itemSubSerieLoaded.items():
                try:
                    widgetNumber=infoMetadatoSubSerie.values().index(tupla[0])
                    self.groups[1].widgets[infoMetadatoSubSerie.keys()[widgetNumber]].value=tupla[1]
                except:
                    pass
                    #print u"el elemento no está"

        self.groups[3].mode='hidden'



        #super(EditItem, self).update()
        #self.groups[3].widgets["tituColec"].value=self.dameTituloColeccionByGSID(COLECCION)
        #if len(self.groups[3].widgets["tituColec"].value) >0:
        #    self.label="Formulario para edición de datos descriptivos de las fuentes primarias de la colección %s"%self.groups[3].widgets["tituColec"].value

        #if colec:
        #    self.groups[3].widgets["coleccion"].value = colec.encode('utf-8')
        #    COLECCION=self.groups[3].widgets["coleccion"].value
        #    self.groups[3].widgets["coleccion"].mode = HIDDEN_MODE

    def dameTituloDeColeccionPorID_GS(self,idGs):
        """dado el id de una colección Greenstone devuelve el título del Objeto Coleccion
        de Plone"""
        
        catalogo=getToolByName(self.context,"portal_catalog")
        
        colecs=catalogo(object_provides=IColeccion.__identifier__)
        for brain in colecs:
            if brain.getObject().GS_ID == idGs:
                return brain.Title
        return ""
        
    def apagrupo(self,grupo):
        for wid in grupo.widgets:
            grupo.widgets[wid].mode=HIDDEN_MODE

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

    @button.buttonAndHandler(u'Guardar')
    def saveHandler(self, action):
        self.saveFlag=self.saveFlag+1
   
        if self.saveFlag<2:
            msj=rutaItem=rutaSubSerie=rutaSerie=""
            subSerieOk=False

            infoMetadatos=infoMetaItem
            #infoMetadatosSerie=infoMetadatosSerie

            data, errors = self.extractData()

            if len(self.groups[3].widgets["subserie"].value)>0:
                subSerieOk=True
                #infoMetadatoSubSerie=infoMetadatoSubSerie

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
                tmpList.append((infoMetaItem[x],itFtext))
                
            dicDatosItem={
                "version":"1",
                "idColec":self.groups[3].widgets["coleccion"].value,
                "ruta":rutaItem,                
                "folder":self.groups[3].widgets["coleccion"].value+"/"+rutaItem.replace("/metadata.xml",""),
                "metadatos":tmpList,
                #"metadatos":[(infoMetaItem[x],self.groups[2].widgets[x].value) for x in infoMetadatos]
                }
                
            #-------- cargo ITEM    
            tmpList=[]
            for x in infoMetadatosSerie:
                itFtext=self.groups[2].widgets[x].value
                if type(itFtext)==type([]):
                    itFtext=itFtext[0]                
                tmpList.append((infoMetadatosSerie[x],itFtext))
            
            dicDatosSerie={
                "version":"1",
                "idColec":self.groups[3].widgets["coleccion"].value,
                "ruta":rutaSerie,                
                "folder":self.groups[3].widgets["coleccion"].value+"/"+rutaSerie.replace("/metadata.xml",""),
                "metadatos":tmpList,                                  
                #"metadatos":[(infoMetadatosSerie[x],self.groups[0].widgets[x].value) for x in infoMetadatosSerie]
            }
            
            if subSerieOk:
                tmpList=[]
                for x in infoMetadatoSubSerie:
                    itFtext=self.groups[1].widgets[x].value
                    if type(itFtext)==type([]):
                        itFtext=itFtext[0]                
                    tmpList.append((infoMetadatoSubSerie[x],itFtext))
                    
                dicDatosSubSerie={
                    "version":"1",
                    "idColec":self.groups[3].widgets["coleccion"].value,
                    "ruta":rutaSubSerie,                    
                    "folder":self.groups[3].widgets["coleccion"].value+"/"+rutaSubSerie.replace("/metadata.xml",""),
                    "metadatos":tmpList
                }
             
            
            self.fsmanager=FSManager()

            flagm=0
            
            
            itemsaved=self.fsmanager.saveFile(dicDatosItem,"item")
            seriesaved=self.fsmanager.saveFile(dicDatosSerie,"serie")
 
            if itemsaved[0]=="error":
                msj="> No se pudo guardar el item en %s"%rutaItem
                flagm+=1

            if seriesaved[0]=="error":
                msj="> No se pudo guardar la serie en %s"%rutaSerie              
               
                flagm+=1                
            
                    
            if subSerieOk:                
                subSeriesaved=self.fsmanager.saveFile(dicDatosSubSerie,"subSerie")
                if subSeriesaved[0]=="error":
                    msj="> No se pudo guardar la sub serie en %s" %rutaSubSerie
                    flagm+=1
                else:
                    subSeriesaved='sin sub serie'
                
                if flagm==0:
                    
                    mandoCorreo=self.emails({'ritem':itemsaved,'rsubserie':subSeriesaved,'rserie':seriesaved})
                    if mandoCorreo:
                        self.msjForm =u"Los cambios fueron guardados correctamente. Se generó una nueva versión de metadatos y se envió un email para control."
                    else:
                        self.msjForm =u"Los cambios fueron guardados. Pero hubo un error al querer enviar el correo."
                else:
                    self.msjForm =u"No se pudieron guardar los cambios... se ha generando reporte"
            else:
                self.status=self.msjForm
        miurl=self.context.REQUEST.URL
        self.context.REQUEST.RESPONSE.redirect(miurl+"?formOk="+self.msjForm.encode('utf8'))

    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""
        global COLECCION
        global SERIE
        global SUBSERIE

        COLECCION=SERIE=SUBSERIE=""        
        self.editOk = False
        self.form._finishedAdd = True
        miurl=self.context.REQUEST.URL
        
        self.context.REQUEST.RESPONSE.redirect(miurl+"?cancel=ok")

        
    def dameTituloColeccionByGSID(self,gsid):
        cata=getToolByName(self.context,"portal_catalog")
        brains=cata(portal_type="arcas.coleccion")
        nombreColeccion=""
        for elem in brains:
            if elem.getObject().GS_ID==gsid:
                nombreColeccion=elem.Title
                break

        return nombreColeccion
           
    def emails(self,datos):        
        sender=MAIL_ADMIN
        mt=getToolByName(self.context,"portal_membership")
        
        nombreColeccion=self.dameTituloColeccionByGSID(self.groups[3].widgets["coleccion"].value)

        operarioMail    = mt.getAuthenticatedMember().getProperty('email',None)
        operarioNombre  = mt.getAuthenticatedMember().getProperty('fullname',None)      
                
        if operarioMail=='':
            operarioMail="pablomusa@gmail.com"

        if operarioNombre=='':
            operarioNombre="Pablo Musa"

        coordinadorMail = MAIL_COORDINADOR
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
        
        
        hhtml = u"<html><head></head><body><h3>Modificación en la coleccion: %s </h3>"%nombreColeccion
        hhtml += u"El usuario: %s, realizó modificaciones en los matadatos de ARCAS.</br>" %operarioNombre.decode("utf8")
        hhtml += u"<p>Esto es un registro básico de lo realizado:</p><ul>"
        hhtml += u"<li><b>Serie:</b><ul>"

        for stra in rutasSerie:
            hhtml += '<li>%s</li>'%stra

        if len(rutasSerie)==1:
            hhtml += '<li>Sin cambios</li>'

        hhtml += "</ul></li>"

        hhtml += u"<li><b>SubSerie:</b><ul>"
        for stra in rutasSubSerie:  
            hhtml += '<li>%s</li>'%stra
            
        if len(rutasSubSerie)==1:
            hhtml += '<li>Sin cambios</li>'
        hhtml += "</ul></li>"

        hhtml += u"<li><b>Item:</b><ul>"
        for stra in rutasItem:            
            hhtml += '<li>%s</li>'%stra

        if len(rutasItem)==1:
            hhtml += '<li>Sin cambios</li>'            
        hhtml += "</ul></li>"

        hhtml += u"</ul><hr/><p>Este es un mail automático, por favor no responder. En caso de errores "
        hhtml += u"comunicarse con mariana@fahce.unlp.edu.ar</p>Gracias.</p>"
        hhtml += u"</br></br><p></p>"
        hhtml += u"</body></html>"

        #Record the MIME types of both parts - text/plain and text/html.
 
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


    

