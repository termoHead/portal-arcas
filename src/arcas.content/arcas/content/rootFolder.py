# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _
from plone.app.textfield import RichText
from five import grok
from zope import schema
from plone.directives import form
from plone.formwidget.contenttree import ContentTreeFieldWidget
from arcas.content.exhibicion import IExhibicion
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.schema import RelationList, RelationChoice
from arcas.content.coleccionesFolder import IColeccionesFolder
from plone.formwidget.contenttree import ObjPathSourceBinder
from plone.app.layout.navigation.interfaces import INavigationRoot
from plone.dexterity.content import Container


class IRootFolder(form.Schema):
    """Una carpeta principal para documentos publicos
    """
    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=True,
    )


    form.widget('exhiDestacada', ContentTreeFieldWidget)
    exhiDestacada = RelationChoice(
        title=u'Selecciones una Exhibicion',
        description=u"Seleccione la exhibicion a destacar",
        source=ObjPathSourceBinder(object_provides=IExhibicion.__identifier__),
        required=False,
    )

class CarpetaRaiz(Container):
    grok.implements(IRootFolder,INavigationRoot)


from Acquisition import aq_inner
from plone.directives.dexterity import DisplayForm
from arcas.content.utils import ColeccionUtils
class View(DisplayForm):
    grok.context(IRootFolder)
    grok.require('zope2.View')


    def getExhiDestacado(self):
        ##recreaFolder= self.getContainer(folder.encode('utf8'))
        ##cuando busca documento hace referencia al campo "documento" que es el destacado del directorio


        try:
            if self.context.exhiDestacada!=None:
                destacado=self.context.exhiDestacada.to_object
                colecTRelated=destacado.coleccionR.to_object
                colecUtils=ColeccionUtils(colecTRelated)
                descrD=destacado.description
                if len(descrD)>250:
                    descrD=descrD[0:descrD[:250].rfind(" ")]+" ..."

                resp={
                    'titulo' : destacado.title,
                    'tituloColec': colecTRelated.title,
                    'descri' : descrD,
                    'exhiurl': destacado.absolute_url(),
                    'curador': colecUtils.dameCurador(),#esta dameCurador funcion ya devuelve una lista,
                    'integrantes': colecUtils.getCoordinadores()+colecUtils.dameIntegrantes()
                }

                return resp
        except :
            print "no hay exhibiciones asiganadas al portlet"
            pass

        return []

    def listExhiUrl(self):
        """Devuelve la url al listado de exhibiciones"""
        from arcas.content.exhibicionesFolder import IExhibicionesFolder
        catalog=getToolByName(self.context,"portal_catalog")
        exlis=catalog(object_provides=IExhibicionesFolder.__identifier__)
        if len(exlis)>0:
            return exlis[0].getURL()
        else:
            return False

    def getColecciones(self):
        ##recreaFolder= self.getContainer(folder.encode('utf8'))
        ##cuando busca documento hace referencia al campo "documento" que es el destacado del directorio
        catalog=getToolByName(self.context,"portal_catalog")
        colList=catalog.searchResults(portal_type='arcas.coleccion',review_state='Publicado')
        resuList=[]
        extraFUrl=""
        extraFT=""
        try:
            for elem in colList:
                destacado=self.context.unrestrictedTraverse(elem.getPath())
                desta_path = '/'.join(destacado.getPhysicalPath())
                cataloDest=catalog.searchResults(path={'query':desta_path , 'depth': 1})

                for carpeta in cataloDest:
                    if carpeta.portal_type=="Folder" and carpeta.Title!="Galería":
                        extraFUrl=carpeta.getURL()
                        extraFT=carpeta.Title
                        break
                descrD=elem.Description
                if len(descrD)>350:
                    descrD=descrD[0:descrD[:350].rfind(" ")]+" ..."

                resuList.append({
                    "titulo":elem.Title,
                    "id":elem.id,
                    "url":elem.getURL(),
                    "description":descrD,
                    "extraFolderUrl":extraFUrl,
                    "extraFolderTitulo":extraFT
                } )
            return resuList
        except :
            print "no hay colecciones asiganadas al portlet"
            pass

    def listColeccUrl(self):
        """Devuelve la url al listado de colecciones"""
        catalog= getToolByName(self.context,"portal_catalog")
        exlis  = catalog(object_provides=IColeccionesFolder.__identifier__)
        if len(exlis)>0:
            return exlis[0].getURL()
        else:
            return False

    def dameNoticias(self):
        """devuelve las noticias"""


        catalog= getToolByName(self.context,"portal_catalog")

        cexto=aq_inner(self.context)

        if hasattr(cexto,"novedades"):
            folder_path = '/'.join(cexto.novedades.getPhysicalPath())
            results = catalog(path={'query': folder_path, 'depth': 1})
            return results
        else:
            return []

    def dameNotiUrl(self):
        """URL a la carpeta de noticias"""
        cexto=aq_inner(self.context)
        if not hasattr(cexto,"novedades"):
            cexto.invokeFactory("Folder","novedades")
            cexto.novedades.title="Novedades"
            cexto.novedades.description="Toda la información referente a ARCAS"

        return cexto.novedades.absolute_url()

    def dameProyectoUrl(self):
        """URL al documento del proyecto"""
        strT="acerca_de_arcas"
        cexto=aq_inner(self.context)
        if not hasattr(cexto,strT):
            cexto.invokeFactory("Folder",strT)
            print "Se creo la carpeta Acerca de "
            cexto.acerca_de_arcas.title="Acerca de Arcas"
            cexto.acerca_de_arcas.description="Información sobre el proyecto"
            cexto.acerca_de_arcas.invokeFactory("Document","el_proyecto_arcas")
            cexto.acerca_de_arcas.el_proyecto_arcas.title="El proyecto ARCAS"


        return cexto.acerca_de_arcas.el_proyecto_arcas.absolute_url()

    def dameTextoDescri(self):
        """Texto de destacado"""
        caracteresCorte=600
        idObject="el_proyecto_arcas"
        catalog=getToolByName(self.context,"portal_catalog")
        brain=catalog(id=idObject)[0]

        texto=brain.getObject().getText()
        if texto>caracteresCorte:
            corteTexto=texto[:caracteresCorte]
            apertura= corteTexto.rfind("<p>")
            cierre  = corteTexto.rfind("</p>")
            if cierre<apertura:
                corteTexto=corteTexto+"</p>"

        return "<p>%s</p>%s" %(brain.Description,corteTexto)