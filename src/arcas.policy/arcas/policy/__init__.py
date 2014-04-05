# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory
_ = MessageFactory("arcas.policy")

ROLES_MESSAGE_FACTORY = MessageFactory('arcas.policy.roles')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
