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

class IAddFiles(form.Schema):
    upFile = NamedFile(title=u"Subir archivo",
    description=u"El archivo con la fuente primaria. Si son muchos, por favor comprima los mismos en un archivo ZIP")
    

class NuevoItemGS(form.SchemaForm):
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    folderNameBase='nuevo_item'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'
    rutaNivelSerie=''
    colecId=''
    version=0

    grok.name('nuevoItemGS')
    grok.require('zope2.View')
    #grok.require('cmf.ListFolderContents')
    #grok.require('arcas.addExhibicion')
    grok.context(IRootFolder)
    schema = IAddFiles    
    fields=field.Fields(IGsMetaItem).select("f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones",
        "f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta")
    ignoreContext = True    
    label       = u"Nueva obra"
    description = u'<div class="formuDescri">Se está agregando una obra nueva</div>'
    
    
    def update(self):
        super(NuevoItemGS, self).update()
        self.colecId=self.request.get('colecId', None)
        colec = self.request.get('colec', None)
        serie = self.request.get('serie', None)
        subserie = self.request.get('subserie', None)
        
        self.widgets["f_ruta"].value=self.request.get('biruta', None)
        self.determinaRutaNivelSerie()
        
        if self.colecId == None:
            self.colecId="puig"
        
        
        if subserie:
            self.description = u'<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span>, subserie: <span class="destacado">%s</span></div>.' %(colec,serie,subserie)
        else:
            self.description = '<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span></div>.'%(colec,serie)
        import pdb
        pdb.set_trace()
        
    def determinaRutaNivelSerie(self):
        """determina la ruta en la que se creara la nueva carpeta"""
        rutaItem=self.widgets["f_ruta"].value 
        arTmp = rutaItem.split("/")
        del arTmp[-1]
        del arTmp[-1]
        rutaSerie = "/".join(arTmp)
        
        #buscarNumeroDeVersion y sumarle un      
        #rutaSerie+='/nuevoItem'+lasVersion        
        self.rutaNivelSerie = self.xmlFileBase+self.colecId+rutaSerie
        

    def dameSigVerisonFolder(self):
        rut=self.rutaNivelSerie
        listado =os.listdir(rut)
        tmp     =["1"]
        listR=[]
        for elem in listado:            
            ex="nuevoItem"
            if elem.find(ex)>-1:
                tmpL=elem.split(ex)                
                listR.append(tmpL[len(tmpL)-1])

        if len(listR)==0:
            return "1"
        else:
            sum=int(listR[len(listR)-1])+1
            return(str(sum))
        
                
    @button.buttonAndHandler(u'Guardar')
    def saveHandler(self, action):        
        lasVersion=self.dameSigVerisonFolder()
        
        file=self.widgets['upFile'].value.headers.fp
        fileName=self.widgets['upFile'].value.filename
        
        if not os.path.exists(finalPath):
            os.makedirs(finalPath)
            
        rutaSerie+='/nuevoItem'+lasVersion
        
        print "guardando en: " +rutaSerie
        #with open(finalPath+'/'+fileName, "w") as f:
        #    f.write(file.getvalue())
        
        
        
        self.status = "Cambios guardados"
        
    
    @button.buttonAndHandler(u"Cancel")
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""
        
        
        
        COLECCION=SERIE=SUBSERIE=""        
        self.status = "Cambios cancelados"
        self.editOk = False
        self.form._finishedAdd = True
        miurl=self.context.REQUEST.URL
        self.context.REQUEST.RESPONSE.redirect(miurl)

        