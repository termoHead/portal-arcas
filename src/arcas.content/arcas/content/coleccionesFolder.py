# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _

from five import grok
from plone.app.textfield import RichText
from zope import schema
from plone.dexterity.content import Container
from plone.app.textfield import RichText

import z3c.form.field
from plone.namedfile.interfaces import IImageScaleTraversable
from plone.namedfile.field import NamedBlobImage
from plone.directives import form
from arcas.content.coleccion import IColeccion
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.utils import ColeccionUtils
class IColeccionesFolder(form.Schema):
    """Carpeta que guarda colecciones"""

    cuerpo = RichText(
        title=_(u"Texto principal"),
        required=False,
    )

from Acquisition import aq_inner
from plone.directives.dexterity   import DisplayForm
from plone.app.vocabularies.users import UsersSource
from Products.CMFCore.utils import getToolByName

class View(DisplayForm):
    grok.context(IColeccionesFolder)
    grok.require('zope2.View')
    grok.name('view')

    def dameListaColecciones(self):
        """Devuelve una Lista con dicccionario de cada coleccion"""
        contexto = self.context.aq_inner

        catalogo=getToolByName(contexto,"portal_catalog")
        result=catalogo(object_provides=IColeccion.__identifier__)

        listados=[]

        for colec in result:
            miOb=contexto.unrestrictedTraverse(colec.getPath())
            colUtils=ColeccionUtils(miOb)
            descrip=colec.Description
            if len(descrip)>280:
                descrip=descrip[:descrip[:280].rfind(" ")]+" ..."

            listados.append({
                "titulo":colec.Title,
                "descri":descrip,
                "url":colec.getURL(),
                "scales":miOb,
                "coors":colUtils.getCoordinadores(),
                "idColec":miOb.GS_ID,
                "urlFuente":colUtils.getUrlAFuente(),
                "altFuente":miOb.altNavegarFuente,}
                )

        return listados


