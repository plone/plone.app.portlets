from .. import PloneMessageFactory as _
from ..portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer


class IClassicPortlet(IPortletDataProvider):
    """A portlet which can render a classic Plone portlet macro"""

    template = schema.ASCIILine(
        title=_("Template"),
        description=_("The template containing the portlet."),
        required=True,
    )

    macro = schema.ASCIILine(
        title=_("Macro"),
        description=_(
            "The macro containing the portlet. " "Leave blank if there is no macro."
        ),
        default="portlet",
        required=False,
    )


@implementer(IClassicPortlet)
class Assignment(base.Assignment):
    def __init__(self, template="", macro=""):
        self.template = template
        self.macro = macro

    @property
    def title(self):
        return self.template


class Renderer(base.Renderer):
    def __init__(self, context, request, view, manager, data):
        self.context = context
        self.request = request
        self.data = data

    render = ViewPageTemplateFile("classic.pt")

    def use_macro(self):
        return bool(self.data.macro)

    def path_expression(self):
        expr = "context/%s" % self.data.template
        if self.use_macro():
            expr += "/macros/%s" % self.data.macro
        return expr


class AddForm(base.AddForm):
    schema = IClassicPortlet
    label = _("Add Classic Portlet")
    description = _("A classic portlet allows you to use legacy portlet " "templates.")

    def create(self, data):
        return Assignment(
            template=data.get("template", ""), macro=data.get("macro", "")
        )


class EditForm(base.EditForm):
    schema = IClassicPortlet
    label = _("Edit Classic Portlet")
    description = _("A classic portlet allows you to use legacy portlet " "templates.")
