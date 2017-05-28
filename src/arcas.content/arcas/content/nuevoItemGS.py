# -*- coding: utf-8 -*-
__author__ = 'Paul'
import os

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

class IAddFiles(form.Schema):
    upFile = NamedFile(title=u"Subir archivo",
    description=u"El archivo con la fuente primaria. Si son muchos, por favor comprima los mismos en un archivo ZIP")
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
    
    version=0

    grok.name('nuevoItemGS')
    grok.require('zope2.View')
    #grok.require('cmf.ListFolderContents')
    #grok.require('arcas.addExhibicion')
    grok.context(IRootFolder)
    schema = IAddFiles
    fields=field.Fields(IGsMetaItem).select("f_titulo","f_autor","f_colaborador","f_edicion","f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones",
        "f_naturaleza","f_alcance","f_ruta","f_anotacion")
    ignoreContext = True
    label       = u"Nueva obra"
    description = u'<div class="formuDescri">Se está agregando una obra nueva </div>'
    
    
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
                self.description = u'<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span>, subserie: <span class="destacado">%s</span>.</div>' %(colec,serie,subserie)
                self.widgets["subSerie"].value=subserie
            else:
                self.description = '<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span></div>.'%(colec,serie)
            
        rutaObra=self.determinaRutaNivelSerie(self.widgets["f_ruta"].value,self.widgets["colecId"].value)        
        self.widgets["rutaNivelObra"].value=rutaObra
      
  

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
        print "----------------"        
        print self.widgets["f_ruta"].value
        print "----------------"
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

        if len(listR)==0:
            return "1"
        else:
            sum=int(listR[len(listR)-1])+1
            return(str(sum))
        
    def showSave(self):
        vva=True
        if 'cancel' in self.request.keys():
            vva=False
        return vva        
        
    @button.buttonAndHandler(u'Guardar',condition=showSave)
    def saveHandler(self, action):
        print "guardando datos"
        flagm=0
        infoMetadatos=infoMetaItem
        data, errors = self.extractData()
        
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
            itFtext=self.widgets[x].value
            if itFtext!="":
                if type(itFtext)==type([]):                    
                    itFtext=itFtext[0]
                tmpList.append((infoMetaItem[x],itFtext))
            
        rutaItem= self.widgets["f_ruta"].value 
        nomSerie=self.widgets["serie"].value
        nomSubSerie=self.widgets["subSerie"].value
        
        dicDatosItem={                   
            "folder":rutaSerie,
            "nombreColeccion":self.dameTituloColeccionByGSID(self.groups[3].widgets["coleccion"].value),
            "nomSerie":nomSerie,
            "nomSubSerie":nomSubSerie,
            "ruta":rutaItem,
            "metadatos":tmpList,            
            }
        
        #guardo el archivo adjunto
        with open(rutaSerie+'/'+fileName, "w+") as f:
            f.write(xfile.getvalue())
        
        
        #guardo el xml
        fsmanager=FSManager()
        itemsaved=fsmanager.saveFileNuevoFile(dicDatosItem)
        
        if itemsaved[0]=="error":
                msj="> No se pudo guardar el item en %s"%rutaSerie
                flagm+=1
                return
                
        mandoMail=self.emails({'itemTitulo':itemsaved,'serieTitulo':subSeriesaved,'rserie':seriesaved})
        
        if mandoMail:        
            self.status = u"Se creó un nuevo registro"
        else:
            self.status = u"Se creó el nuevo registro, pero no se pudo enviar el correo"
        
    
    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""
        COLECCION=SERIE=SUBSERIE=""        
        self.status = "Cambios cancelados"        
        self.form._finishedAdd = True
        miurl=self.context.REQUEST.URL+"?cancel=ok"            
        self.context.REQUEST.RESPONSE.redirect(miurl)


    def emails(self,datos):        
        msj=Cartero()
        loMando=msj.sendAlta(datos)
        return loMnando