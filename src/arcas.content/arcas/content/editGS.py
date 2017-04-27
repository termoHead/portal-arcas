 # -*- coding: utf-8 -*-
__author__ = 'Paul'
#"lucene-jdbm-demo",



from plone.autoform import directives
from arcas.content.rootFolder import IRootFolder
from Products.CMFPlone.utils import safe_unicode

from five import grok
from plone.directives import form

from zope import schema
from z3c.form import button
from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.interfaces import HIDDEN_MODE, DISPLAY_MODE, INPUT_MODE
from Products.CMFCore.interfaces import ISiteRoot
from Products.statusmessages.interfaces import IStatusMessage
from plone.app.textfield import RichText
from plone.app.textfield.value import RichTextValue

from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from z3c.form import action
from zope.component import getMultiAdapter
from zope.schema.interfaces import IContextSourceBinder
from zope.interface import directlyProvides
from plone.supermodel import model


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from Products.CMFCore.utils import getToolByName


from arcas.content.GSWManager import ClienteGS

from arcas.content.config import infoMetadatosSerie
from arcas.content.config import infoMetadatoSubSerie
from arcas.content.config import infoMetaItem
from arcas.content.FSManager import FSManager
COLECCION=""
SERIE=""
SUBSERIE=""


def serie_vocab(self):
    global COLECCION
    if COLECCION=="":
        return  SimpleVocabulary([])
    terms=[]
    cl=ClienteGS()
    lista=cl.getSeries(COLECCION)
    for pair in lista:
        if pair["value"]!=False or  pair["value"]!=True or pair["value"]!="true" or  pair["value"]!="false": 
            terms.append(SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]))
    return SimpleVocabulary(terms)

def subserie_vocab(self):
    global SERIE
    global COLECCION       
    
    if COLECCION!="" and SERIE!="":
        cl=ClienteGS()        
        tieneSub=cl.tieneSubSerie(COLECCION)
        terms=[]
        if tieneSub:
            lista=cl.getDocsFromSerie(COLECCION,SERIE)            
            for pair in lista:   
                if pair["value"]!=False or pair["value"]!=True or pair["value"]!="true" or  pair["value"]!="false":
                    terms.append(SimpleTerm(value=pair["value"], token=pair["value"], title=pair["title"]))
            return SimpleVocabulary(terms)
   
    return  SimpleVocabulary([])
    
def item_vocab(self):
    global SERIE
    global SUBSERIE
    global COLECCION        
    if COLECCION!="" and SUBSERIE!="":    
        cl=ClienteGS()        
        tieneSub=cl.tieneSubSerie(COLECCION)
        terms=[]
        if tieneSub:
            lista=cl.getDocsFromSubSerie(COLECCION,SUBSERIE)            
            for pair in lista:
                terms.append(SimpleTerm(value=pair["value"], 
token=pair["value"], title=pair["title"]))
            return SimpleVocabulary(terms)
        else:
            lista=cl.getDocsFromSerie(COLECCION,SERIE)
            for pair in lista:                
                terms.append(SimpleTerm(value=pair["value"], 
token=pair["value"], title=pair["title"]))
            return SimpleVocabulary(terms)
    return  SimpleVocabulary([])

iso_idiomas=SimpleVocabulary([
    SimpleTerm(value=u'ay', title=(u'aimara')),
    SimpleTerm(value=u'de', title=(u'alemán')),
    SimpleTerm(value=u'es', title=(u'español (o castellano)')),
    SimpleTerm(value=u'fr', title=(u'francés')),
    SimpleTerm(value=u'el', title=(u'griego (moderno)')),
    SimpleTerm(value=u'gn', title=(u'guaraní')),
    SimpleTerm(value=u'en', title=(u'inglés')),
    SimpleTerm(value=u'it', title=(u'italiano')),
    SimpleTerm(value=u'la', title=(u'latín')),
    SimpleTerm(value=u'pt', title=(u'portugués')),
    SimpleTerm(value=u'qu', title=(u'quechua'))
    ])

def coleccionesVocab(context):
    "colecciones en "
    cl=ClienteGS()
    mt=getToolByName(context,"portal_membership")
    catalogo=getToolByName(context,"portal_catalog")
    idColec = mt.getAuthenticatedMember().getProperty('participaEn',None)
    colectL=[]
    for elem in idColec.split(","):        
        colec=catalogo(id=elem)[0]
        colectL.append(colec.getObject().GS_ID)
        
    
    lista=cl.dameListadoColecciones()
    
    terms = [lista[0]]    
    for idGs in colectL:
        if idGs in lista:    
            terms.append(idGs)            
    if len(terms)>1:
        return SimpleVocabulary.fromValues(terms)
    else:
        return SimpleVocabulary.fromValues(lista)

directlyProvides(coleccionesVocab, IContextSourceBinder)
directlyProvides(serie_vocab, IContextSourceBinder)
directlyProvides(subserie_vocab, IContextSourceBinder)
directlyProvides(item_vocab, IContextSourceBinder)



class IGsMetaItem(form.Schema):
    model.fieldset('Obra',
        label=(u"Descripción del Item"),
        
    fields=["f_titulo","f_autor","f_colaborador","f_edicion","f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones",
        "f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta"]
    )
    
        
    
    f_titulo= schema.TextLine(
        title=u"Título",
        description=u"Título del documento",
        required=True,
    )
    f_autor= schema.TextLine(
        title=u"Autor",        
        required=True,
    )
    
    f_colaborador= schema.Text(
        title=u'Colaboradore/s',
        description=u'Agregar un colaborador por linea, en formato: apellido, nombre',
        required=False,
    )
    f_edicion= schema.TextLine(
        title=u"Edición",        
        required=False,
    )
    f_fechaCreacion= schema.TextLine(
        title=u"Fecha",
        description=u"Fecha de creacion del documento",
        required=False,
    )
    
    f_lugarCreacion= schema.TextLine(
        title=u"Lugar",
        description=u"Lugar de creacion del documento",
        required=False,
    )
    f_descFisica= schema.TextLine(
        title=u"Descripción física",
        description=u"Descripción física del documento",
        required=False,
    )
    
    f_dimensiones= schema.TextLine(
        title=u"Dimensiones",        
        required=False,
    )
    
    form.widget(f_idioma=CheckBoxFieldWidget)
    f_idioma= schema.List(
        title=u"Idioma",
        description=u"Los valores que se desean asignar debe.",
        value_type=schema.Choice(vocabulary=iso_idiomas),
        required=False,
    )
    
    f_naturaleza= schema.TextLine(
        title=u"Naturaleza",
        description=u"Naturaleza del documento",
        required=False,
    )
    
    f_alcance= schema.TextLine(
        title=u"Alcance",        
        required=False,
    )
    
    directives.mode(f_ruta='hidden')
    f_ruta= schema.TextLine(
        title=u"Ruta al xml",
        description=u"no se que es... sera el título del documento",
        required=False,
    ) 
    form.widget('f_anotacion', klass='recargaForm',size=5)
    f_anotacion = schema.Text(title=u"Anotación",required=True,)

class IGsSubSerie(form.Schema):
    model.fieldset('Subserie',
        label=(u"Descripción de la sub Serie"),
        fields=["sub_titulo","sub_alcance","sub_anotacion",]
    )
    sub_titulo= schema.TextLine(
        title=u"Título",
        description=u"titulo de la sub serie",
        required=False,
    )  
    sub_alcance= schema.TextLine(
        title=u"Alcance",
        description=u"Alcance de la subserie",
        required=False,
    ) 
    sub_anotacion=schema.TextLine(
        title=u"Anotación",
        required=False,
    ) 
    
class IGsMetaSerie(form.Schema):
    model.fieldset('Item',label=(u"Descripción de la Serie"),
        
fields=["s_titulo","s_temporal","s_autor","s_extension","s_caracteristicas",
"s_alcance","s_lenguaiso"]
    )
    s_titulo= schema.TextLine(title=u"Titulo",
        description=u"Título de la serie",required=False,) 
        
    s_temporal= schema.TextLine(title=u"Cobertura temporal",
        description=u"Extensión de tiempo que cubre la serie",required=False,) 
        
    s_autor= schema.TextLine(title=u"Autor",
        description=u"Autor de la Serie",required=False,) 
        
    s_extension= schema.TextLine(title=u"Extensión",
        description=u"no se que es... sera el título del documento",required=False,)
   
    s_caracteristicas= schema.TextLine(title=u"Descripción física",
        description=u"Cantidad de items de la serie",required=False,)
        
    s_alcance= schema.TextLine(title=u"Alcance",
        description=u"no se que es... sera el título del documento",required=False,)
        
    s_lenguaiso = schema.Choice(title=u"Idioma",vocabulary=iso_idiomas,description=u"Idioma de la serie",required=False,)


    
class IEditGS(form.Schema, IGsMetaSerie , IGsSubSerie,IGsMetaItem ):
    """Campos del formulario de edición de un documento Greenston3 en el 
import!"""    
    model.fieldset('Selección de ítem Serie ',
        label=(u"Elija una serie para editar"),
        fields=["coleccion","serie","subserie","obra","obraTmp","tituColec"]
    )    
    
    form.widget('coleccion', klass='recargaForm')
    coleccion= schema.Choice(
        title=u"Colección",
        description=u"Elija una colección para editar",
        source=coleccionesVocab,
        required=True,
    )
    serie = schema.Choice(
        title=u"Serie",
        description=u"Elija una obra para editar",        
        source=serie_vocab,
        required=False,
    )
    subserie= schema.Choice(
        title=u"Sub Serie",
        description=u"Elija una sub serie para editar",        
        source=subserie_vocab,
        required=False,
    )
    obra = schema.Choice(
        title=u"Obra",
        description=u"Elija una obra para editar",        
        source=item_vocab,
        required=False,
    )
    directives.mode(obraTmp='hidden')
    obraTmp= schema.TextLine(
        title=u"obraTmp",
        description=u"una pavada",
        required=False,
    )    
    directives.mode(tituColec='hidden')
    tituColec= schema.TextLine(
        title=u"Título",
        description=u"título de la colección que está siendo editada",
        required=False,
    )


    

class EditGS(form.SchemaForm):
    """
       Edita un documento de Greenstone3 desde el import!
    """
    xmlFileBase  ='/usr/local/Greenstone3/web/sites/localsite/collect/'
    xmlFileResto ='/import/co.1/se.1/su.1/ar.1/it.1/'
    xmlFileName='metadata.xml'
    
    grok.name('editGs')
    grok.require('zope2.View')
    #grok.require('cmf.ListFolderContents')
    #grok.require('arcas.addExhibicion')
    grok.context(IRootFolder)
    schema = IEditGS
    
    ignoreContext = True    
    label       = u"Formulario para edición de datos descriptivos de las fuentes primarias"
    description = u'<div class="formuDescri">Los datos que usted va a editar se actualizarán una vez hayan sido revisados y aceptados\
                    para su inclusión/modificación por el equipo técnico de ARCAS. Recibirá un mail con la modificación \
                    por Usted realizada y cuando haya sido actualizado en el Portal público.<br \/>\
                    En todos los casos, el formulario mostrará para editar la versión pública. Si necesita modificar \
                    una versión generada por usted aún no publicada, utilice la información recibida por mail para \
                    recuperar los datos de las versiones intermedias.</div>\
                    '
    fsmanager   = ""
    coleccion   = "cordemia"
    serie       = ""
    obra        = ""
    saveFlag    = 0
    msjForm     = ""
    
    
    #lsw=["f_fechaCreacion","f_lugarCreacion","f_descFisica","f_dimensiones","f_idioma","f_naturaleza","f_alcance","f_anotacion","f_ruta"]

   
    editOk=False
    
    def update(self):
        global COLECCION
        global SERIE
        global SUBSERIE        
        super(EditGS, self).update()
        """
            tmpG=[]
            ordenGrupos=[u"Metadatos del Item",u"Metadatos de la Sub Serie", 
            u"Metadatos de la serie"]
            for grupo in ordenGrupos:
                for elem in self.groups:
                    if elem.label==grupo:
                        tmpG.append(elem)
            tmpG.append(self.groups[3])
            self.groups=tuple(tmpG)
        """
        
        COLECCION=SERIE=SUBSERIE=""
        colec = self.request.get('coleccion', None)
        self.xmlFileResto= self.request.get('coleccion', None)
        
        if(len(self.groups[3].widgets["coleccion"].value)>0):
                COLECCION=self.groups[3].widgets["coleccion"].value[0]
                
        if colec:
            self.groups[3].widgets["coleccion"].value = colec.encode('utf-8')
            COLECCION=self.groups[3].widgets["coleccion"].value

        if(len(self.groups[3].widgets["serie"].value)>0):
            if self.groups[3].widgets["serie"].value[0] != "--NOVALUE--":
                SERIE=self.groups[3].widgets["serie"].value[0]

        if(len(self.groups[3].widgets["subserie"].value)>0):
            if self.groups[3].widgets["subserie"].value[0] != "--NOVALUE--":
                SUBSERIE=self.groups[3].widgets["subserie"].value[0]
        
        super(EditGS, self).update()
        
        self.groups[3].widgets["tituColec"].value=self.dameTituloColeccionByGSID(COLECCION)
        if len(self.groups[3].widgets["tituColec"].value) >0:            
            self.label="Formulario para edición de datos descriptivos de las fuentes primarias de la colección %s"%self.groups[3].widgets["tituColec"].value
        if colec:
            self.groups[3].widgets["coleccion"].value = colec.encode('utf-8')
            COLECCION=self.groups[3].widgets["coleccion"].value
            self.groups[3].widgets["coleccion"].mode = HIDDEN_MODE

        
    def apagrupo(self,grupo):
        for wid in grupo.widgets:            
            grupo.widgets[wid].mode=HIDDEN_MODE
        
    def showObras(self):
        # Set a custom widget for a field for this form instance only       
        if self.groups[0].widgets["f_ruta"].value!=u"":
            return True
        else:
            return False

    def showSave(self):
        if "form.buttons.editar" in self.request.form:
            return True
        else:
            return False

    @button.buttonAndHandler(u'Guardar',condition=showObras)
    def saveHandler(self, action):
        self.saveFlag=self.saveFlag+1
   
        if self.saveFlag<2:
            msj=rutaItem=rutaSubSerie=rutaSerie=""
            subSerieOk=False

            infoMetadatos=infoMetaItem
            #infoMetadatosSerie=infoMetadatosSerie

            data, errors = self.extractData()

            if len(self.groups[3].widgets["subserie"].value)>0:
                subSerieOk=True
                #infoMetadatoSubSerie=infoMetadatoSubSerie

            if errors:
                self.status = self.formErrorsMessage
                return
                
            #rutaArchivos
            rutaItem= self.groups[0].widgets["f_ruta"].value        
            
            if subSerieOk:            
                arTmp = rutaItem.split("/")
                del arTmp[-2]
                del arTmp[-2]
                rutaSerie = "/".join(arTmp)
                
                arTmp = rutaItem.split("/")
                del arTmp[-2]
                rutaSubSerie = "/".join(arTmp)
            else:
                arTmp = rutaItem.split("/")
                del arTmp[-2]
                rutaSerie = "/".join(arTmp)

            
            
            #-------- cargo ITEM
            tmpList=[]
            for x in infoMetadatos:
                itFtext=self.groups[0].widgets[x].value
                if type(itFtext)==type([]):
                    itFtext=itFtext[0]                
                tmpList.append((infoMetaItem[x],itFtext))
                
            dicDatosItem={
                "version":"1",
                "idColec":self.groups[3].widgets["coleccion"].value[0],
                "ruta":rutaItem,                
                "folder":self.groups[3].widgets["coleccion"].value[0]+"/"+rutaItem.replace("/metadata.xml",""),
                "metadatos":tmpList,
                #"metadatos":[(infoMetaItem[x],self.groups[2].widgets[x].value) for x in infoMetadatos]
                }
                
            #-------- cargo ITEM    
            tmpList=[]
            for x in infoMetadatosSerie:
                itFtext=self.groups[2].widgets[x].value
                if type(itFtext)==type([]):
                    itFtext=itFtext[0]                
                tmpList.append((infoMetadatosSerie[x],itFtext))
            
            dicDatosSerie={
                "version":"1",
                "idColec":self.groups[3].widgets["coleccion"].value[0],
                "ruta":rutaSerie,                
                "folder":self.groups[3].widgets["coleccion"].value[0]+"/"+rutaSerie.replace("/metadata.xml",""),
                "metadatos":tmpList,                
                #"metadatos":[(infoMetadatosSerie[x],self.groups[0].widgets[x].value) for x in infoMetadatosSerie]
            }
            
            if subSerieOk:
                tmpList=[]
                for x in infoMetadatoSubSerie:
                    itFtext=self.groups[1].widgets[x].value
                    if type(itFtext)==type([]):
                        itFtext=itFtext[0]                
                    tmpList.append((infoMetadatoSubSerie[x],itFtext))
                    
                dicDatosSubSerie={
                    "version":"1",
                    "idColec":self.groups[3].widgets["coleccion"].value[0],
                    "ruta":rutaSubSerie,                    
                    "folder":self.groups[3].widgets["coleccion"].value[0]+"/"+rutaSubSerie.replace("/metadata.xml",""),
                    "metadatos":tmpList
                }
             
            
            self.fsmanager=FSManager()

            flagm=0
            
            
            itemsaved=self.fsmanager.saveFile(dicDatosItem,"item")
            seriesaved=self.fsmanager.saveFile(dicDatosSerie,"serie")
 
            if itemsaved[0]=="error":
                msj="> No se pudo guardar el item en %s"%rutaItem
                flagm+=1

            if seriesaved[0]=="error":
                msj="> No se pudo guardar la serie en %s"%rutaSerie              
               
                flagm+=1                
            
                    
            if subSerieOk:            
                
                subSeriesaved=self.fsmanager.saveFile(dicDatosSubSerie,"subSerie")
                if subSeriesaved[0]=="error":
                    msj="> No se pudo guardar la sub serie en %s" %rutaSubSerie  
                  
                    flagm+=1
                else:
                    subSeriesaved='sin sub serie'
                
                if flagm==0:
                    
                    mandoCorreo=self.emails({'ritem':itemsaved,'rsubserie':subSeriesaved,'rserie':seriesaved})
                    if mandoCorreo:
                        self.msjForm =u"Los cambios fueron guardados correctamente. Se generó una nueva versión de metadatos y se envió un email para control."
                    else:
                        self.msjForm =u"Los cambios fueron guardados. Pero hubo un error al querer enviar el correo."
                else:
                    self.msjForm =u"No se pudieron guardar los cambios... se ha generando reporte"
            else:
                self.status=self.msjForm


    @button.buttonAndHandler(u"Cancel",condition=showObras)
    def handleCancel(self, action):
        """User cancelled. Redirect back to the front page."""
        global COLECCION
        global SERIE
        global SUBSERIE

        COLECCION=SERIE=SUBSERIE=""
        self.status = "Cambios cancelados"
        self.editOk = False
        self.form._finishedAdd = True
        miurl=self.context.REQUEST.URL
        self.context.REQUEST.RESPONSE.redirect(miurl)

        
    def dameTituloColeccionByGSID(self,gsid):
        cata=getToolByName(self.context,"portal_catalog")
        brains=cata(portal_type="arcas.coleccion")
        nombreColeccion=""
        for elem in brains:
            if elem.getObject().GS_ID==gsid:
                nombreColeccion=elem.Title
                break

        return nombreColeccion
           
    def emails(self,datos):        
        sender="admin@arcas.unlp.edu.ar"
        mt=getToolByName(self.context,"portal_membership")
        
        nombreColeccion=self.dameTituloColeccionByGSID(self.groups[3].widgets["coleccion"].value[0])

        operarioMail    = mt.getAuthenticatedMember().getProperty('email',None)
        operarioNombre  = mt.getAuthenticatedMember().getProperty('fullname',None)      
                
        if operarioMail=='':
            operarioMail="pablomusa@gmail.com"

        if operarioNombre=='':
            operarioNombre="Pablo Musa"

        coordinadorMail = "mariana@fahce.unlp.edu.ar"
        reciver=[operarioMail,coordinadorMail]

        rutasItem =  datos["ritem"]
        rutasSerie =  datos["rserie"]
        rutasSubSerie =  datos["rsubserie"]

        # Create message container - the correct MIME type is multipart/alternative.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "[ARCAS] Cambios en los metadatos de un registro"
        msg['From'] = sender
        msg['To'] = reciver[0]+','+reciver[1]

        # Create the body of the message (a plain-text and an HTML version).
        text = "Hola!\nSe modificaron metadatos en el Greenston de ARCAS.\n Los Archivos son: %s\n %s \n%s" %(rutasSerie,rutasSubSerie,rutasItem)
        
        
        hhtml = u"<html><head></head><body><h3>Modificación en la coleccion: %s </h3>"%nombreColeccion
        hhtml += u"El usuario: %s, realizó modificaciones en los matadatos de ARCAS.</br>" %operarioNombre.decode("utf8")
        hhtml += u"<p>Esto es un registro básico de lo realizado:</p><ul>"
        hhtml += u"<li><b>Serie:</b><ul>"

        for stra in rutasSerie:
            hhtml += '<li>%s</li>'%stra

        if len(rutasSerie)==1:
            hhtml += '<li>Sin cambios</li>'

        hhtml += "</ul></li>"

        hhtml += u"<li><b>SubSerie:</b><ul>"
        for stra in rutasSubSerie:  
            hhtml += '<li>%s</li>'%stra
            
        if len(rutasSubSerie)==1:
            hhtml += '<li>Sin cambios</li>'
        hhtml += "</ul></li>"

        hhtml += u"<li><b>Item:</b><ul>"
        for stra in rutasItem:            
            hhtml += '<li>%s</li>'%stra

        if len(rutasItem)==1:
            hhtml += '<li>Sin cambios</li>'            
        hhtml += "</ul></li>"

        hhtml += u"</ul><hr/><p>Este es un mail automático, por favor no responder. En caso de errores "
        hhtml += u"comunicarse con mariana@fahce.unlp.edu.ar</p>Gracias.</p>"
        hhtml += u"</br></br><p></p>"
        hhtml += u"</body></html>"

        #Record the MIME types of both parts - text/plain and text/html.
 
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(hhtml.encode('utf8'), 'html')
        msg.attach(part1)
        msg.attach(part2)
        
        try:
            s = smtplib.SMTP('localhost')
            # sendmail function takes 3 arguments: sender's address, recipient's address
            # and message to send - here it is sent as one string.
            s.sendmail(sender, reciver, msg.as_string())
            s.quit()
            return True
        except Exception:
            print "Error: unable to send email"
            return False


    

