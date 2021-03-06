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
from z3c.form.browser.checkbox import CheckBoxFieldWidget
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

from arcas.content.editGS import IGsMetaItem,iso_idiomas

from arcas.content.FSManager import FSManager
from plone.namedfile.field import NamedFile
from z3c.form import field, group
from arcas.content.config import infoMetaItem, MAIL_ADMIN ,MAIL_COORDINADOR
from arcas.content.cartero import Cartero
#from patoolib import *

from ZODB.blob import Blob



class IAddFiles(form.Schema):
    upFile = NamedFile(
        title=u"Subir archivo",
        description=u"El archivo con la fuente primaria. Si son muchos, por favor comprima los mismos en un archivo ZIP",
        required=True,)
        
        
    directives.mode(rutaNivelObra='hidden')    
    rutaNivelObra= schema.TextLine(
        title=u"Ruta de la obra",
        description=u"ruta para armar la carpeta nueva",
        required=False,
    )   
    directives.mode(colecId='hidden')
    colecId= schema.TextLine(
        title=u"Id colección",
        description=u"Colección",
        required=False,
    )
    
    directives.mode(colec='hidden')
    colec= schema.TextLine(
        title=u"coleccion",
        description=u"Colección",
        required=False,
    )
    directives.mode(serie='hidden')
    serie= schema.TextLine(
        title=u"serie",
        description=u"Colección",
        required=False,
    )
    directives.mode(subSerie='hidden')
    subSerie= schema.TextLine(
        title=u"subserie",
        description=u"Colección",
        required=False,
    )
    form.widget(f_idioma=CheckBoxFieldWidget)
    f_idioma= schema.List(
        title=u"Idioma",
        description=u"Los valores que se desean asignar debe.",
        value_type=schema.Choice(vocabulary=iso_idiomas),
        required=False,
    )

from plone.z3cform.fieldsets.utils import move

class NuevoItemGS(form.SchemaForm):
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    folderNameBase='nuevo_item'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'    
    autoGroups = False
    version=0

    grok.name('nuevoItemGS')
    grok.require('zope2.View')
    #grok.require('cmf.ListFolderContents')
    #grok.require('arcas.addExhibicion')
    grok.context(IRootFolder)
    #schema = IAddFiles
    schema =IAddFiles    
    fields=field.Fields(IGsMetaItem).select("f_titulo","f_autor","f_colaborador","f_edicion","f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones","f_naturaleza","f_alcance","f_ruta","f_anotacion")
    
    ignoreContext = True
    label       = u"Nueva obra"
    description = u'<div class="formuDescri">Se está agregando una obra nueva </div>'
    description = u'<div class="formuDescri">Los datos que usted va a editar se actualizarán una vez hayan sido revisados y aceptados\
                    para su inclusión/modificación por el equipo técnico de ARCAS. Recibirá un mail con la modificación \
                    por Usted realizada y cuando haya sido actualizado en el Portal público.<br \/>\
                    En todos los casos, el formulario mostrará para editar la versión pública. Si necesita modificar \
                    una versión generada por usted aún no publicada, utilice la información recibida por mail para \
                    recuperar los datos de las versiones intermedias.</div>\
                    '
    
    def update(self):
        super(NuevoItemGS, self).update()
        
        if self.request.get('cancel', None):
            return
        
        if self.request.get('biruta', None):
            self.widgets["f_ruta"].value=self.request.get('biruta', None)    
        if self.request.get('colecId', None):
            self.widgets["colecId"].value=self.request.get('colecId', None)
            colec = self.request.get('colec', None)
            serie = self.request.get('serie', None)
            subserie = self.request.get('subserie', None)
            self.widgets["colec"].value=colec
            self.widgets["serie"].value=serie
            
            if subserie:
                self.description += u'<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span>, subserie: <span class="destacado">%s</span>.</div>' %(colec,serie,subserie)
                self.widgets["subSerie"].value=subserie
            else:
                self.description = '<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span></div>.'%(colec,serie)
            
        rutaObra=self.determinaRutaNivelSerie(self.widgets["f_ruta"].value,self.widgets["colecId"].value)        
        self.widgets["rutaNivelObra"].value=rutaObra
        self.widgets["f_ruta"].mode=HIDDEN_MODE
  

    def tmlpaaaaa(self):
        
        colec = self.request.get('colec', None)
        serie = self.request.get('serie', None)
        subserie = self.request.get('subserie', None)
        self.widgets["f_ruta"].value=self.request.get('biruta', None)        
        
        if self.colecId == None:
            print "forzando puig"
            self.colecId="puig"
        
        
        #self.rutaNivelSerie=self.determinaRutaNivelSerie(self.widgets["f_ruta"].value)
        if self.widgets["rutaNivelObra"].value!= "":
            self.widgets["rutaNivelObra"].value=self.determinaRutaNivelSerie(self.widgets["f_ruta"].value)                

        print self.widgets["f_ruta"].value

        if subserie:
            self.description = u'<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span>, subserie: <span class="destacado">%s</span></div>.' %(colec,serie,subserie)
        else:
            self.description = '<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span></div>.'%(colec,serie)
        
        
    def determinaRutaNivelSerie(self,tmpRuta,idColect):
        """determina la ruta en la que se creara la nueva carpeta"""
        rutaItem=tmpRuta
        arTmp = rutaItem.split("/")
        del arTmp[-1]
        del arTmp[-1]
        rutaSerie = "/".join(arTmp)
        
        #buscarNumeroDeVersion y sumarle un
        #rutaSerie+='/nuevoItem'+lasVersion
        return self.xmlFileBase+idColect+"/"+rutaSerie

    def dameSigVerisonFolder(self):
        rut=self.widgets["rutaNivelObra"].value
        listado =os.listdir(rut)
        tmp     =["1"]
        listR=[]

        
        for elem in listado:
            ex="nuevoItem"
            if elem.find(ex)>-1 and elem.find(".")<0:
                tmpL=elem.split(ex)
                listR.append(tmpL[len(tmpL)-1])
        import pdb
        pdb.set_trace()
        if len(listR)==0:
            return "1"
        else:
            sum=len(listR)+1
            return str(sum)
        
    def showSave(self):
        vva=True
        if 'cancel' in self.request.keys():
            vva=False
        return vva
        
    @button.buttonAndHandler(u'Guardar',condition=showSave)
    def saveHandler(self, action):
        mt=getToolByName(self.context,"portal_membership")   
        operarioMail    = mt.getAuthenticatedMember().getProperty('email',None)
        operarioNombre  = mt.getAuthenticatedMember().getProperty('fullname',None)
        operarioDict={'nombre':operarioNombre,'mail':operarioMail}
        flagm=0
        infoMetadatos=infoMetaItem
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        #genera el nombre de la nueva carpeta
        numLastVersion=self.dameSigVerisonFolder()
        rutaSerie=self.widgets["rutaNivelObra"].value

        xfile   =self.widgets['upFile'].value.headers.fp
        fileName=self.widgets['upFile'].value.filename
        rutaSerie+='/nuevoItem'+numLastVersion

        if not os.path.exists(rutaSerie):
            os.makedirs(rutaSerie)

        #Recorro los campos y los agrego la lista tmpList
        tmpList=[]

        for x in infoMetadatos:
            if "form.widgets."+x in self.request.form:
                itFtext=self.request.form["form.widgets."+x]

                if x == "f_autor" and len(itFtext)>0:
                    tmpC=[]
                    for elem in itFtext.split("\r\n"):
                        tmpC.append(elem) 
                    tmpList.append((infoMetaItem[x],tmpC))
                    
                elif x == "f_colaborador" and len(itFtext)>0:
                    tmpC=[]
                    for elem in itFtext.split("\r\n"):
                        tmpC.append(elem) 
                    tmpList.append((infoMetaItem[x],tmpC))
                elif itFtext!="":
                    tmpList.append((infoMetaItem[x],itFtext))
                    
        rutaItem    = self.widgets["f_ruta"].value
        nomSerie    =self.widgets["serie"].value
        nomSubSerie =self.widgets["subSerie"].value
        nombreColeccion=self.dameTituloDeColeccionPorID_GS(self.request.form["form.widgets.colecId"])
        
        dicDatosItem={
            "folder":rutaSerie,
            "nombreColeccion":nombreColeccion,
            "nomSerie":nomSerie,
            "nomSubSerie":nomSubSerie,
            "ruta":rutaItem,
            "metadatos":tmpList,
            }

        #guardo el archivo adjunto
        rutaFinal=rutaSerie+'/'+fileName
        
        try:
            ppax=xfile.getvalue()
            with open(rutaFinal, "w+") as f:
                f.write(xfile.getvalue())            
            # Method exists, and was used.  
        except AttributeError:
            # Method does not exist.  What now?
            print "error"
        

        #guardo el xml
        fsmanager=FSManager()
        itemsaved=fsmanager.saveFileNuevoFile(dicDatosItem,operarioDict)

        if itemsaved[0]=="error":
                self.msjForm="> No se pudo guardar el item en %s"%rutaSerie
                flagm+=1
                return

        mandoMail=self.emails({'ruta':itemsaved[0],'serie':nomSubSerie,'coleccion':nombreColeccion},operarioDict)

        if mandoMail:
            self.msjForm = u"El registro se creó con éxito."
        else:
            self.msjForm = u"Se creó un nuevo registro, pero no se pudo enviar el correo."

        miurltmp=self.context.REQUEST.URL
        miurl   ="/".join(miurltmp.split("/")[:-2])
        self.context.REQUEST.RESPONSE.redirect(miurl+"/formsOk_view?mensaje="+self.msjForm.encode('utf8'))


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

    def showSave(self):
        vva=True
        if 'cancel' in self.request.keys():
            vva=False
        return vva
    
    
    
    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""
        COLECCION=SERIE=SUBSERIE=""        
        self.status = "Cambios cancelados"        
        self.form._finishedAdd = True
        miurl=self.context.REQUEST.URL+"/formsCancel_view?cancel= La edición fue cancelada"            
        self.context.REQUEST.RESPONSE.redirect(miurl)


    def emails(self,datos,operarioDict):        
        msj=Cartero(self.context,operarioDict)
        loMando=msj.sendAlta(datos)
        return loMando
