# -*- coding: utf-8 -*-
__author__ = 'Paul'
from arcas.content import ArcasMessageFactory as _
#La constantea es la base para un documento de greenstone
#luego viene la colección elegida puig y la cadena fija "/document"
#URL_GREENSTON_DOC="http://g3:8383/greenstone3/library/collection/"
URL_GREENSTON_DOC="http://arcas.fahce.unlp.edu.ar:8383/greenstone3/library/collection/"



from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
TIPOS_COLECCION = SimpleVocabulary(
    [SimpleTerm(value=u'0', title=_(u'Autor')),
     SimpleTerm(value=u'1', title=_(u'Corpus Linguisticos'))
     ]
    )


#metadatos para el formulario de edicion y carga
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

infoMetaItem={ 'f_fechaCreacion':'ae.itemcoberturatemporal',
    'f_lugarCreacion':'bi.lugar',
    'f_descFisica':'ae.itemdescripcionfisica',
    'f_dimensiones':'ae.itemdimension',
    'f_idioma':'ae.itemlenguaiso',
    'f_naturaleza':'ae.itemnaturaleza',
    'f_alcance':'ae.itemalcance',
    'f_anotacion':'bi.anotacionitem',
    'f_ruta':'bi.ruta'}

itemTitles=[u'Fecha',u'Lugar',u'Descripción física',u'Dimensiones',u'Idioma',u'Naturaleza',u'Alcance',u'Anotación','Ruta Archivo']


 

