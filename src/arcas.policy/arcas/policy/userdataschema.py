# -*- coding: utf-8 -*-
from zope.interface import Interface, implements
from zope import schema
from plone.directives import form
from arcas.policy import _
from plone.app.users.userdataschema import IUserDataSchemaProvider
from plone.app.users.userdataschema import IUserDataSchema

def validateAccept(value):
    if not value == True:
        return False
    return True

class UserDataSchemaProvider(object):
    implements(IUserDataSchemaProvider)

    def getSchema(self):
        """
        """
        return IEnhancedUserDataSchema

class IEnhancedUserDataSchema(IUserDataSchema):
    """ Use all the fields from the default user data schema, and add various
    extra fields.
    """

    esUNLP= schema.Bool(
        title=u'¿Pertenece a la UNLP?',
        description=u"Marque la opcion correspondiente",
        required=True
        )

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
        value_type=schema.Choice(source="arcas.policy.ColeccionesVocab"),
        required=False,
        )

    form.mode(colecCoordina='display')
    colecAsignadas=schema.Set(
            title=u'Participa como integrante',
            description=u"La lista muestra las colecciones en las que participa actualmente.",
            value_type=schema.Choice(source="arcas.policy.ColeccionesVocab"),
            required=False,
            readonly=True
    )

    form.mode(colecCoordina='display')
    colecCoordina=schema.Set(
        title=u'Participa como coordinador',
        description=u"La lista muestra las colecciones que administra.",
        value_type=schema.Choice(source="arcas.policy.ColeccionesVocab"),
        required=False,
        readonly=True
    )
