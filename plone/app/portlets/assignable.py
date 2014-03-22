from zope.interface import implementer
from zope.component import adapter
from zope.annotation.interfaces import IAnnotations

from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignable
from plone.portlets.interfaces import IPortletManager

from plone.portlets.constants import CONTEXT_ASSIGNMENT_KEY
from plone.portlets.constants import CONTEXT_CATEGORY

from plone.app.portlets.storage import PortletAssignmentMapping


@adapter(ILocalPortletAssignable, IPortletManager)
@implementer(IPortletAssignmentMapping)
def localPortletAssignmentMappingAdapter(context, manager):
    """Zope 2 version of the localPortletAssignmentMappingAdapter factory.
    """
    annotations = IAnnotations(context)
    local = annotations.get(CONTEXT_ASSIGNMENT_KEY, {})
    portlets = local.get(manager.__name__, None)
    if portlets is None:
        # Return new mapping without storing it yet,
        # but pass along the context so it can be stored
        # if an assignment is added.
        portlets = PortletAssignmentMapping(
            manager=manager.__name__,
            category=CONTEXT_CATEGORY,
            context=context)

    # XXX: For graceful migration
    if not getattr(portlets, '__manager__', ''):
        portlets.__manager__ = manager.__name__

    if not getattr(portlets, '__category__', ''):
        portlets.__category__ = CONTEXT_CATEGORY

    return portlets
