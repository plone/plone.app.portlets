# Import PloneMessageFactory to create messages in the plone domain
from zope.i18nmessageid import MessageFactory
import pkg_resources

PloneMessageFactory = MessageFactory('plone')

try:
    pkg_resources.get_distribution('plone.app.event')
except pkg_resources.DistributionNotFound:
    HAS_PLONE_APP_EVENT = False
else:
    HAS_PLONE_APP_EVENT = True
