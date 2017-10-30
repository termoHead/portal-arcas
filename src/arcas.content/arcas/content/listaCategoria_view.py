from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName

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
        
        

    # by default call will call self.index() method which is mapped
    # to ViewPageTemplateFile specified in ZCML
    #def __call__():
    #
    def getCat(self):        
        
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog.searchResults({'portal_type': 'arcas.content.categoria'})
        dato=[]
        for e in results:
            dato.append({
            'titulo':e.Title,
            'descri':e.Description,
            'id':e.id,
            })
        
        return dato

