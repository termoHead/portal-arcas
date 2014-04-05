# -*- coding: utf-8 -*-
__author__ = 'Paul'
from five import grok
from arcas.content.config import URL_GREENSTON_DOC
from arcas.content.eventos import PREFIJO_COOR_GROUP
from arcas.content.behaviors import IColecGroupName
from plone.app.vocabularies.users import UsersSource
from plone.memoize.instance import memoize
from zope.i18n import translate
from zope.i18nmessageid import MessageFactory
from zope.interface import implements

from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Acquisition import aq_get
import unicodedata
from Products.CMFCore.utils import getToolByName
from arcas.content.exhibicion import IExhibicion
from  arcas.content.curador import ICurador
_ = MessageFactory('plone')
from Acquisition import aq_inner
from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from zope.security import checkPermission
from zc.relation.interfaces import ICatalog

class CanalesVocabulary(object):
    implements(IVocabularyFactory)

    def __call__(self,context):
        items = []

        site = context
        return self._data(site)

    @memoize
    def _data(self,contexto):
        """devuleve los resultados de la base"""

        catalogo = getToolByName(contexto, 'portal_catalog', None)
        query = dict(object_provides=IExhibicion.__identifier__)
        result=[]
        for folder in catalogo(query):
            titulito=self.elimina_tildes(folder.Title.decode('utf8'))
            idcito=folder.id
            urlito=folder.getPath()
            result.append(SimpleTerm(urlito,idcito))
        return SimpleVocabulary(result)

    def elimina_tildes(self,s):
        return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

ExhibicionesVocabFactory = CanalesVocabulary()





class GroupMembers(object):
    """Context source binder to provide a vocabulary of users in a given
    group.
    """
    implements(IVocabularyFactory)

    def __init__(self, group_name):
        self.group_name = group_name

    def __call__(self, context):
        acl_users = getToolByName(context, 'acl_users')
        group = acl_users.getGroupById(self.group_name)
        terms = []

        if group is not None:
            for member_id in group.getMemberIds():
                user = acl_users.getUserById(member_id)
                if user is not None:
                    member_name = user.getProperty('fullname') or member_id
                    terms.append(SimpleVocabulary.createTerm(member_id, str(member_id), member_name))

        return SimpleVocabulary(terms)


GroupMembersVocabFactory = GroupMembers("Staff")
#CategoriasVocabFactory = CategoriasVocab()









class ColeccionUtils(object):

    def __init__(self,colec):
        self.coleccion=colec

    def getUrlAFuente(self):
        """devuelv la dirección a la fuente primaria"""
        coleccion=self.coleccion
        baseURL=URL_GREENSTON_DOC+coleccion.GS_ID+"/browse/CL1"
        return baseURL


    def getCoordinadores(self):
        """Devuelve los curadores de la coleción"""

        coleccion=self.coleccion
        idG=self.dameGrupo(coleccion).replace("_g",PREFIJO_COOR_GROUP)

        groups_tool = getToolByName(self.coleccion, 'portal_groups')
        mtool = getToolByName(self.coleccion, 'portal_membership')

        try:
            grupoObj=groups_tool.getGroupById(idG)
        except :
            print "La vista intenta buscar un grupo: %s, que no existe" %idG
            return None

        infoCoor = []
        userssource = UsersSource(grupoObj)

        for coordina in grupoObj.getGroupMembers():
            infoCoor.append({'type' : 'user',
                             'id'   : coordina.id,
                             'title': coordina.getProperty('fullname', None) or coordina.id,
                             'email': coordina.getProperty('email'),
                             'img'  : mtool.getPersonalPortrait(id=coordina.id),
                             })
        return infoCoor

    def dameGrupo(self,colec):

        colec=self.coleccion
        ppa=IColecGroupName(colec)
        return ppa.groupName



    def dameCurador(self):
        """devuelve el curador de una coleccion en lista"""
        coleccion=self.coleccion
        ls=[]
        catalogo=getToolByName(coleccion,"portal_catalog")
        query={"path":"/".join(coleccion.getPhysicalPath()),'object_provides':ICurador.__identifier__}
        result  =catalogo(query)

        for elem in result:
            try:
                miOb=coleccion.unrestrictedTraverse(elem.getPath())
                ls.append(miOb)
            except :
                print "error al buscar el curador"

        return ls

    def dameIntegrantes(self):
        coleccion=self.coleccion
        idG=self.dameGrupo(coleccion)

        groups_tool = getToolByName(self.coleccion, 'portal_groups')
        mtool = getToolByName(self.coleccion, 'portal_membership')

        try:
            grupoObj=groups_tool.getGroupById(idG)
        except :
            print "La vista intenta buscar un grupo: %s, que no existe" %idG
            return None

        infoCoor = []
        userssource = UsersSource(grupoObj)

        for integrante in grupoObj.getGroupMembers():
            infoCoor.append({'type' : 'user',
                             'id'   : integrante.id,
                             'title': integrante.getProperty('fullname', None) or integrante.id,
                             'email': integrante.getProperty('email'),
                             'img'  : mtool.getPersonalPortrait(id=integrante.id),
                             })
        return infoCoor

    def dameExhibicionesR(self):
        return self.back_references(self.coleccion,"coleccionR")

    def back_references(self,source_object, attribute_name):
        """ Return back references from source object on specified attribute_name """
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []

        for rel in catalog.findRelations(
            dict(to_id=intids.getId(aq_inner(source_object)),
                from_attribute=attribute_name)  ):

            obj = intids.queryObject(rel.from_id)
            if obj is not None and checkPermission('zope2.View', obj):
                result.append(obj)
        return result