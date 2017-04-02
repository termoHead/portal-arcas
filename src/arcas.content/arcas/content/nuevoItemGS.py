# -*- coding: utf-8 -*-
__author__ = 'Paul'
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


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFCore.utils import getToolByName

from arcas.content.editGS import IGsMetaItem,iso_idiomas

from arcas.content.FSManager import FSManager

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
    schema = IGsMetaItem
    ignoreContext = True    
    label       = u"Nueva obra"
    description = u'<div class="formuDescri">Se está agregando una obra nueva</div>'
    
    
    def update(self):
        super(NuevoItemGS, self).update()
        colec = self.request.get('colec', None)
        serie = self.request.get('serie', None)
	subserie = self.request.get('subserie', None)	
        self.groups[0].widgets["f_ruta"].value=self.request.get('biruta', None)
        
        if subserie:
            self.description = u'<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span>, subserie: <span class="destacado">%s</span></div>.' %(colec,serie,subserie)
        else:
            self.description = '<div class="descriForm">Se agregará una nueva obra a la colección <span class="destacado">%s</span>, serie: <span class="destacado">%s</span></div>.'%(colec,serie)


    @button.buttonAndHandler(u'Guardar')
    def saveHandler(self, action):      
        
        print self.xmlFileBase+"//"+self.groups[0].widgets["f_ruta"].value        
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

        