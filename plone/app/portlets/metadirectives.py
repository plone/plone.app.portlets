from . import PloneMessageFactory as _
from plone.portlets.interfaces import IPortletManager
from zope import schema
from zope.configuration import fields as configuration_fields
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserView
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPortletDirective(Interface):
    """Directive which registers a new portlet type.

    The portlet should also be installed into a site using a GenericSetup
    portlets.xml file, for example.
    """

    name = schema.TextLine(
        title=_("Name"),
        description=_("A unique name for the portlet. Also used for its add view."),
        required=True,
    )

    interface = configuration_fields.GlobalInterface(
        title=_("Assignment type interface"),
        description=_("Should correspond to the public interface of the assignment"),
        required=True,
    )

    assignment = configuration_fields.GlobalObject(
        title=_("Assignment class"),
        description=_("A persistent class storing the portlet assignment"),
        required=True,
    )

    view_permission = schema.TextLine(
        title=_("View permission"),
        description=_("Permission used for viewing the portlet."),
        required=False,
        default="zope2.View",
    )

    edit_permission = schema.TextLine(
        title=_("Edit permission"),
        description=_("Permission used for editing the portlet assignment."),
        required=False,
        default="plone.app.portlets.ManageOwnPortlets",
    )

    renderer = configuration_fields.GlobalObject(
        title=_("Renderer"),
        description=_("A class which renders the portlet data provider"),
        required=True,
    )

    addview = configuration_fields.GlobalObject(
        title=_("Add view"),
        description=_("View used to add the assignment object"),
        required=True,
    )

    editview = configuration_fields.GlobalObject(
        title=_("Edit view"),
        description=_("View used to edit the assignment object (if appropriate)"),
        required=False,
    )


class IPortletRendererDirective(Interface):
    """Register a portlet renderer, i.e. a different view of a portlet"""

    # The portlet data provider type must be given

    portlet = configuration_fields.GlobalObject(
        title=_("Portlet data provider type for which this renderer is used"),
        description=_("An interface or class"),
        required=True,
    )

    # Use either class or template to specify the custom renderer

    class_ = configuration_fields.GlobalObject(
        title=_("Class"),
        description=_("A class acting as the renderer."),
        required=False,
    )

    template = configuration_fields.Path(
        title=_("The name of a template that implements the renderer."),
        description=_(
            "If given, the default renderer for this portlet will be used, but with this template"
        ),
        required=False,
    )

    # Use these to discriminate the renderer.

    for_ = configuration_fields.GlobalObject(
        title=_("Context object type for which this renderer is used"),
        description=_("""An interface or class"""),
        required=False,
        default=Interface,
    )

    layer = configuration_fields.GlobalObject(
        title=_("Browser layer for which this renderer is used"),
        description=_("""An interface or class"""),
        required=False,
        default=IDefaultBrowserLayer,
    )

    view = configuration_fields.GlobalObject(
        title=_("Browser view type for this this renderer is used"),
        description=_("An interface or class"),
        required=False,
        default=IBrowserView,
    )

    manager = configuration_fields.GlobalObject(
        title=_("Portlet manager type for which this renderer is used"),
        description=_("An interface or class"),
        required=False,
        default=IPortletManager,
    )
