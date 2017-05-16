# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _
#La constantea es la base para un documento de greenstone
#luego viene la colección elegida puig y la cadena fija "/document"
#URL_GREENSTON_DOC="http://g3:8383/greenstone3/library/collection/"
URL_GREENSTON_DOC="http://arcas.fahce.unlp.edu.ar/greenstone3/library/collection/"

#------------------------
#Dirección de correo que figura como enviador de mails automáticos
#se usan en nuevoItemGs.py y editItem.py
MAIL_ADMIN= u"admin@arcas.unlp.edu.ar"
#Dirección de correo a quien se envía copia de la edición y creación de Registros Greenstone
MAIL_COORDINADOR= u"mariana@fahce.unlp.edu.ar"
#------------------------
#metadatos para el formulario de edicion y carga | nuevoItemGs.py y editItem.py
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
TIPOS_COLECCION = SimpleVocabulary(
    [SimpleTerm(value=u'0', title=_(u'Autor')),
     SimpleTerm(value=u'1', title=_(u'Corpus Linguisticos'))
     ]
    )
infoMetadatosSerie={'s_titulo':'ae.serietitulo',
    's_temporal':'ae.seriecoberturatemporal',
    's_extension':'ae.fileextension',
    's_caracteristicas':'ae.seriedescripcionfisica',
    's_autor':'ae.serieautor',
    's_alcance':'ae.seriealcance',
    's_lenguaiso':'ae.serielenguaiso'}

serieTitle=[u'Titulo',u'Cobertura temporal',u'Extensión',u'Descripción física',u'Autor',u'Alcance',u'Idioma']    
infoMetadatoSubSerie={'sub_titulo':'ae.subserietitulo','sub_alcance' :'ae.subserieautor','sub_anotacion':'ae.subserielenguaiso'}
subSerieTitles=[u'Título',u'Alcance',u'Anotación']
infoMetaItem={ 
    'f_titulo':'ae.itemtitulo',
    'f_autor':'ae.itemautor',
    'f_colaborador':'ae.itemcolaborador',
    'f_edicion':'ae.itemedicion',
    'f_fechaCreacion':'ae.itemcoberturatemporal',
    'f_lugarCreacion':'bi.lugar',
    'f_descFisica':'ae.itemdescripcionfisica',
    'f_dimensiones':'ae.itemdimension',
    'f_idioma':'ae.itemlenguaiso',
    'f_naturaleza':'ae.itemnaturaleza',
    'f_alcance':'ae.itemalcance',
    'f_anotacion':'bi.anotacionitem',
    'f_ruta':'bi.ruta'}
itemTitles=[u'Titulo',u'Autor',u'Colaboradores',u'Edición',u'Fecha',u'Lugar',u'Descripción física',u'Dimensiones',u'Idioma',u'Naturaleza',u'Alcance',u'Anotación','Ruta Archivo']


 

