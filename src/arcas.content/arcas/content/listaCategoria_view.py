from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from arcas.content.config import COLOR_COLECCION



class ListaCategoriaView(BrowserView):

    def __init__(self, context, request):
        """ Initialize context and request as view multi adaption parameters.

        Note that the BrowserView constructor does this for you.
        This step here is just to show how view receives its context and
        request parameter. You do not need to write __init__() for your
        views.
        """
        self.context = context
        self.request = request
        
    def autorizado(self):
        mt=getToolByName(self.context,"portal_membership")
        session_id=mt.getAuthenticatedMember().id

        if session_id == 'acl_users':
            return False
        
        agrupos=mt.getAuthenticatedMember().getGroups()
        print agrupos
        if "Site Administrators" in agrupos or "Administrators" in agrupos or session_id=="admin":
            return True
        else:
            return False
        
        
        
    # by default call will call self.index() method which is mapped
    # to ViewPageTemplateFile specified in ZCML
    #def __call__():
    #
    def getCat(self):        
        self.usados=[]
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults({'portal_type': 'arcas.content.categoria'})
        dato=[]
        for e in results:
            colorN=""
            for col in COLOR_COLECCION:
                if col.value== e.getObject().color:
                    colorN=col.title
            dato.append({
            'titulo':e.Title,
            'descri':e.Description,
            'color':e.getObject().color,
            'colorN':colorN,
            'id':e.id,
            })
            self.usados.append(e.getObject().color)
        return dato
        
    def dameColores(self):        
        colores=[]
        for emc in COLOR_COLECCION:
            if emc.value not in self.usados:
                colores.append({'value':emc.value,'title':emc.title})
        
        return colores

