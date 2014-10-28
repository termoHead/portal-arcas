# -*- coding: utf-8 -*-
__author__ = 'Paul'
from plone.app.users.browser.personalpreferences import UserDataPanelAdapter
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.CMFCore.utils import getToolByName
from arcas.content.eventos import PREFIJO_COOR_POTENCIAL
from zope.component import getMultiAdapter


def on_save(event):
    """ cuando se cambia el perfil de usuario"""
    estaAsignadoPotencial=False

    from plone.app.controlpanel.interfaces import IConfigurationChangedEvent
    if IConfigurationChangedEvent.providedBy(event):
        groups_tool=getToolByName(event.context,"portal_groups")
        member_tool=getToolByName(event.context,"portal_membership")
        miId=member_tool.getAuthenticatedMember().getId()


        if event.data.has_key("participaEn"):
            if event.data["participaEn"]:
                for nomColect in event.data["participaEn"]:
                    nGid=nomColect+PREFIJO_COOR_POTENCIAL
                    grupPotencial=groups_tool.getGroupById(nGid)

                    groups_tool.addPrincipalToGroup(miId, nGid)

        """Determian si està asignado a la colección que eligió"""




        print "particpa en "
