__author__ = 'Paul'
from Products.CMFCore.utils import getToolByName

def setupGroups(portal):
    acl_users = getToolByName(portal, 'acl_users')
    if not acl_users.searchGroups(name='Coordinadores'):
        gtool = getToolByName(portal, 'portal_groups')
        gtool.addGroup('Coordinadores', roles=['Coordinador'])

def importVarious(context):
    """Miscellanous steps import handle
    """
    if context.readDataFile('arcas.policy-various.txt') is None:
        return

    portal = context.getSite()
    setupGroups(portal)