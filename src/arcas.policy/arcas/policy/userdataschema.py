# -*- coding: utf-8 -*-
from zope.interface import Interface, implements
from zope import schema
from plone.directives import form
from arcas.policy import _
from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchema
from plone.namedfile.field import NamedBlobFile
from zope.schema.vocabulary import SimpleVocabulary,SimpleTerm
from zope.component import getUtility, queryUtility
from zope.schema.interfaces import IVocabularyFactory

def validateAccept(value):
    if not value == True:
        return False
    return True
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.vocabulary import SimpleVocabulary



class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        return IEnhancedUserDataSchema


class IEnhancedUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """

    tipoUsuario = schema.Set(
        title=u'Tipo de usuario',
        description=u'Si desea marcar más de una opcion, oprima CTRL+Click',
        value_type=schema.Choice(values = [
            'Seleccione una opcion',
            'Alumno',
            'Docente',
            'Investigador',
            'Otro',
            ],),

        required=True,
        )
    form.write_permission(participaEn='cmf.ManagePortal')
    participaEn =schema.Set(
        title=u'Colecciones de su interés',
        description=u"Elija la o las Colecciones en las que desea participar. Si desea marcar más de una opcion, oprima CTRL+Click",
        value_type=schema.Choice(source="ColeccionesVocab"),
        required=False,
        )

    form.write_permission(participaEn='cmf.ManagePortal')
    participaEn =schema.Set(
        title=u'Colecciones de su interés',
        description=u"Elija la o las Colecciones en las que desea participar. Si desea marcar más de una opcion, oprima CTRL+Click",
        value_type=schema.Choice(source="ColeccionesVocab"),
        required=False,
        )

    form.mode(colecCoordina='display')
    colecAsignadas=schema.Set(
            title=u'Ya participa en:',
            description=u"La lista muestra las colecciones en las que participa actualmente.",
            value_type=schema.Choice(source="ColeccionesVocab"),
            required=False,
            readonly=True
    )

    form.mode(colecCoordina='display')
    colecCoordina=schema.Set(
        title=u'Es coordinador de:',
        description=u"La lista muestra las colecciones que administra.",
        #value_type=schema.Choice(source=arcas.policy.ColeccionesVocab),
        value_type=schema.Choice(values = [
            'Seleccione una opcion',
            'Alumno',
            'Docente',
            'Investigador',
            'Otro',
            ]),
        required=False,
        readonly=True
    )
    """
    full_cv = schema.Bytes(
        title=u"Full CV",   
        description=u"Suba un archivo con su curriculum para descargar",        
        required=False
    )


    form.write_permission(participaEn='cmf.ManagePortal')
    participaEn =schema.Set(
        title=u'Colecciones de su interés',
        description=u"Elija la o las Colecciones en las que desea participar. Si desea marcar más de una opcion, oprima CTRL+Click",
        value_type=schema.Choice(source="arcas.policy.ColeccionesVocab"),
        required=False,
        )

    form.mode(colecCoordina='display')
    colecAsignadas=schema.Set(
            title=u'Ya participa en:',
            description=u"La lista muestra las colecciones en las que participa actualmente.",
            value_type=schema.Choice(source="arcas.policy.ColeccionesVocab"),
            required=False,
            readonly=True
    )

    form.mode(colecCoordina='display')
    colecCoordina=schema.Set(
        title=u'Es coordinador de:',
        description=u"La lista muestra las colecciones que administra.",
        #value_type=schema.Choice(source=arcas.policy.ColeccionesVocab),
        value_type=schema.Choice(values = [
            'Seleccione una opcion',
            'Alumno',
            'Docente',
            'Investigador',
            'Otro',
            ]),
        required=False,
        readonly=True
    )

 """
