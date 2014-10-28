# -*- coding: utf-8 -*-
__author__ = 'Paul'
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from arcas.content.eventos import PREFIJO_COOR_POTENCIAL
from zope.component import getMultiAdapter


class EnhancedUserDataPanelAdapter(UserDataPanelAdapter):
    """
    """


    def get_tipoUsuario(self):
        valorL=self.context.getProperty('tipoUsuario', '')
        if len(valorL)>0:
            if isinstance(valorL,list):
                value=','.join(valorL)
            else:
                value = valorL.split(',')
        else:
            return ""
        return value
    def set_tipoUsuario(self, value):
        valueX=','.join(value)
        return self.context.setMemberProperties({'tipoUsuario': valueX})
    tipoUsuario = property(get_tipoUsuario, set_tipoUsuario)

    def get_participaEn(self):
        valorL=self.context.getProperty('participaEn', '')
        if len(valorL)>0:
            if isinstance(valorL,list):
                value=','.join(valorL)
            else:
                value = valorL.split(',')
        else:
            return ""
        return value
    def set_participaEn(self, value):
        valueX=','.join(value)
        return self.context.setMemberProperties({'participaEn': valueX})
    participaEn = property(get_participaEn, set_participaEn)


    def get_colecCoordina(self):
        valorL=self.context.getProperty('colecAsignadas', '')
        if len(valorL)>0:
            if isinstance(valorL,list):
                value=','.join(valorL)
            else:
                value = valorL.split(',')
        else:
            return ""
        return value

    def set_colecCoordina(self, value):
        valueX=','.join(value)
        return self.context.setMemberProperties({'colecAsignadas': valueX})
    colecCoordina= property(get_colecCoordina, set_colecCoordina)

    def get_colecAsignadas(self):
        valorL=self.context.getProperty('participaEn', '')
        if len(valorL)>0:
            if isinstance(valorL,list):
                value=','.join(valorL)
            else:
                value = valorL.split(',')
        else:
            return ""
        return value
    def set_colecAsignadas(self, value):
        valueX=','.join(value)
        return self.context.setMemberProperties({'participaEn': valueX})
    colecAsignadas = property(get_colecAsignadas, set_colecAsignadas)


    def get_full_cv(self,context):
        return self.context.getProperty('full_cv')

    def set_full_cv(self, value):

        roota=self.context.portal_url.getPortalObject()
        rootPath=roota.getPhysicalPath()[1]
        idUser=self.context.id
        carpetaUser=self.context.unrestrictedTraverse("/"+rootPath+"/Members/"+idUser)

        return self.context.setMemberProperties({'full_cv': value})

    full_cv= property(get_full_cv, set_full_cv)
