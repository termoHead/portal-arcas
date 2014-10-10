from Acquisition import aq_inner
from AccessControl import Unauthorized

from zope.component import getUtility
from zope.component import adapts
from zope.formlib.interfaces import WidgetInputError
from zope.formlib.itemswidgets import DropdownWidget
from zope.interface import implements, Interface
from zope import schema
from zope.schema import ValidationError
from zope.schema import Choice
from zope.schema import Bool
from zope.formlib import form

from Products.CMFCore.interfaces import ISiteRoot
from Products.CMFCore.utils import getToolByName

from plone.app.users.browser.account import AccountPanelForm
from plone.app.users.browser.account import AccountPanelSchemaAdapter
from plone.app.users.userdataschema import IUserDataSchemaProvider

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFDefault.formlib.widgets import FileUploadWidget
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import set_own_login_name, safe_unicode
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from arcas.content.rootFolder import IRootFolder

class IPersonalPreferences(Interface):

    """ Provide schema for personalize form """

    visible_ids = Bool(
        title=_(u'label_edit_short_names',
            default=u'Allow editing of Short Names'),
        description=_(
            u'help_display_names',
            default=(u'Determines if Short Names (also known '
                     u'as IDs) are changable when editing items. If Short '
                     u'Names are not displayed, they will be generated '
                     u'automatically.')),
        required=False
           )

    wysiwyg_editor = Choice(
        title=_(u'label_wysiwyg_editor', default=u'Wysiwyg editor'),
        description=_(u'help_wysiwyg_editor',
                       default=u'Wysiwyg editor to use.'),
        vocabulary="plone.app.vocabularies.AvailableEditors",
        required=False,
        )

    ext_editor = Bool(
        title=_(u'label_ext_editor', default=u'Enable external editing'),
        description=_(u'help_content_ext_editor',
           default=u'When checked, an option will be '
           'made visible on each page which allows you '
           'to edit content with your favorite editor '
           'instead of using browser-based editors. This '
           'requires an additional application, most often '
           'ExternalEditor or ZopeEditManager, installed '
           'client-side. Ask your administrator for more '
           'information if needed.'),
        )

    language = Choice(
        title=_(u'label_language', default=u'Language'),
        description=_(u'help_preferred_language', u'Your preferred language.'),
        vocabulary="plone.app.vocabularies.AvailableContentLanguages",
        required=False
        )


class PersonalPreferencesPanelAdapter(AccountPanelSchemaAdapter):

    def get_wysiwyg_editor(self):
        return self.context.getProperty('wysiwyg_editor', '')

    def set_wysiwyg_editor(self, value):
        # No value means "use site default", portal_memberdata expects
        # an empty string, not a None.  (As opposed to "None" which
        # means "no editor")
        if value is None:
            value = ''
        return self.context.setMemberProperties({'wysiwyg_editor': value})

    wysiwyg_editor = property(get_wysiwyg_editor, set_wysiwyg_editor)

    def get_ext_editor(self):
        return self.context.getProperty('ext_editor', '')

    def set_ext_editor(self, value):
        return self.context.setMemberProperties({'ext_editor': value})

    ext_editor = property(get_ext_editor, set_ext_editor)

    def get_visible_ids(self):
        return self.context.getProperty('visible_ids', '')

    def set_visible_ids(self, value):
        return self.context.setMemberProperties({'visible_ids': value})

    visible_ids = property(get_visible_ids, set_visible_ids)

    def get_language(self):
        return self.context.getProperty('language', '')

    def set_language(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties({'language': value})

    language = property(get_language, set_language)


def LanguageWidget(field, request):
    """ Create selector with languages vocab """

    widget = DropdownWidget(field, field.vocabulary, request)
    widget._messageNoValue = _(u"vocabulary-missing-single-value-for-edit",
                        u"Language neutral (site default)")
    return widget


def WysiwygEditorWidget(field, request):

    """ Create selector with available editors """

    widget = DropdownWidget(field, field.vocabulary, request)
    widget._messageNoValue = _(u"vocabulary-available-editor-novalue",
                        u"Use site default")
    return widget


class PersonalPreferencesPanel(AccountPanelForm):
    """ Implementation of personalize form that uses formlib """

    label = _(u"heading_my_preferences", default=u"Personal Preferences")
    description = _(u"description_my_preferences",
                    default=u"Your personal settings.")
    form_name = _(u'legend_personal_details', u'Personal Details')

    form_fields = form.FormFields(IPersonalPreferences)
    form_fields['language'].custom_widget = LanguageWidget
    form_fields['wysiwyg_editor'].custom_widget = WysiwygEditorWidget

    def setUpWidgets(self, ignore_request=False):
        """ Hide the visible_ids field based on portal_properties.
        """
        context = aq_inner(self.context)
        properties = getToolByName(context, 'portal_properties')
        siteProperties = properties.site_properties

        if not siteProperties.visible_ids:
            self.hidden_widgets.append('visible_ids')

        super(PersonalPreferencesPanel, self).setUpWidgets(ignore_request)


class PersonalPreferencesConfiglet(PersonalPreferencesPanel):
    """ """
    template = ViewPageTemplateFile('account-configlet.pt')


class UserDataPanelAdapter(AccountPanelSchemaAdapter):

    def _getProperty(self, name):
        """ PlonePAS encodes all unicode coming from PropertySheets.
            Decode before sending to formlib. """
        value = self.context.getProperty(name, '')
        if value:
            return safe_unicode(value)
        return value

    def get_fullname(self):
        return self._getProperty('fullname')

    def set_fullname(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties({'fullname': value})

    fullname = property(get_fullname, set_fullname)

    def get_email(self):
        return self._getProperty('email')

    def set_email(self, value):
        if value is None:
            value = ''
        props = getToolByName(self, 'portal_properties').site_properties
        if props.getProperty('use_email_as_login'):
            set_own_login_name(self.context, value)
        return self.context.setMemberProperties({'email': value})

    email = property(get_email, set_email)

    def get_home_page(self):
        return self._getProperty('home_page')

    def set_home_page(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties({'home_page': value})

    home_page = property(get_home_page, set_home_page)

    def get_description(self):
        return self._getProperty('description')

    def set_description(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties({'description': value})

    description = property(get_description, set_description)

    def get_location(self):
        return self._getProperty('location')

    def set_location(self, value):
        if value is None:
            value = ''
        return self.context.setMemberProperties({'location': value})

    location = property(get_location, set_location)

    def get_portrait(self):
        mtool = getToolByName(self.context, 'portal_membership')
        portrait = mtool.getPersonalPortrait(self.context.id)
        return portrait

    def set_portrait(self, value):
        if value:
            context = aq_inner(self.context)
            context.portal_membership.changeMemberPortrait(value, context.id)

    portrait = property(get_portrait, set_portrait)

    def get_pdelete(self):
        pass

    def set_pdelete(self, value):
        if value:
            context = aq_inner(self.context)
            context.portal_membership.deletePersonalPortrait(context.id)

    pdelete = property(get_pdelete, set_pdelete)


class UserDataPanel(AccountPanelForm):

    label = _(u'title_personal_information_form',
              default=u'Personal Information')
    form_name = _(u'User Data Form')

    def validate(self, action, data):
        context = aq_inner(self.context)
        errors = super(UserDataPanel, self).validate(action, data)

        if not self.widgets['email'].error():
            reg_tool = getToolByName(context, 'portal_registration')
            props = getToolByName(context, 'portal_properties')
            if props.site_properties.getProperty('use_email_as_login'):
                err_str = ''
                try:
                    id_allowed = reg_tool.isMemberIdAllowed(data['email'])
                except Unauthorized:
                    err_str = _('message_email_cannot_change',
                                default=(u"Sorry, you are not allowed to "
                                         u"change your email address."))
                else:
                    if not id_allowed:
                        # Keeping your email the same (which happens when you
                        # change something else on the personalize form) or
                        # changing it back to your login name, is fine.
                        membership = getToolByName(context,
                                                   'portal_membership')
                        if self.userid:
                            member = membership.getMemberById(self.userid)
                        else:
                            member = membership.getAuthenticatedMember()
                        if data['email'] not in (member.getId(),
                                                 member.getUserName()):
                            err_str = _(
                                'message_email_in_use',
                                default=(
                                    u"The email address you selected is "
                                    u"already in use or is not valid as login "
                                    u"name. Please choose another."))

                if err_str:
                    errors.append(WidgetInputError(
                        'email', u'label_email', err_str))
                    self.widgets['email'].error = err_str

        return errors

    @property
    def description(self):
        mt = getToolByName(self.context, 'portal_membership')
        if self.userid and (self.userid != mt.getAuthenticatedMember().id):
            #editing someone else's profile
            return _(u'description_personal_information_form_otheruser',
                     default='Change personal information for $name',
                     mapping={'name': self.userid})
        else:
            #editing my own profile
            return _(u'description_personal_information_form',
                     default='Change your personal information')

    def __init__(self, context, request):
        """
            Load the UserDataSchema at view time.
            (Because doing getUtility for IUserDataSchemaProvider fails at startup time.)
        """
        contenedor=context
        if IRootFolder.providedBy(contenedor):
            contenedor=context.aq_parent

        super(UserDataPanel, self).__init__(contenedor, request)
        util = getUtility(IUserDataSchemaProvider)
        schema = util.getSchema()

        self.form_fields = form.FormFields(schema)
        self.form_fields['portrait'].custom_widget = FileUploadWidget

    def getPortrait(self):
        context = aq_inner(self.context)
        return context.portal_membership.getPersonalPortrait()


class UserDataConfiglet(UserDataPanel):
    """ """
    template = ViewPageTemplateFile('account-configlet.pt')

