from .. import PloneMessageFactory as _
from ..portlets import base
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.interface import implementer

import re


# Legitimate Classic-portlet template/macro names are plain traversal steps
# (e.g. "portlet_recent", "@@view", "content-core"). They must never contain
# TALES metacharacters such as "|", ":" (python:/string:), whitespace or
# parentheses, which would otherwise allow a TALES expression injection.
_SAFE_NAME = re.compile(r"^[A-Za-z0-9_@.\-/]*$")


def _valid_name(value):
    if value and not _SAFE_NAME.match(value):
        raise schema.ValidationError(
            "Only letters, digits and the characters _ @ . - / are allowed."
        )
    return True


class IClassicPortlet(IPortletDataProvider):
    """A portlet which can render a classic Plone portlet macro"""

    template = schema.ASCIILine(
        title=_("Template"),
        description=_("The template containing the portlet."),
        required=True,
        constraint=_valid_name,
    )

    macro = schema.ASCIILine(
        title=_("Macro"),
        description=_(
            "The macro containing the portlet. " "Leave blank if there is no macro."
        ),
        default="portlet",
        required=False,
        constraint=_valid_name,
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
        """Build the TALES *path* expression used to render the portlet.

        The ``template`` and ``macro`` fields are validated against a strict
        whitelist (see ``_valid_name``) which forbids ``:`` and ``|``. This
        guarantees the resulting string can only ever be a plain path
        traversal: it cannot introduce a TALES expression type
        (``python:``/``string:``/...) nor the ``|`` fallback operator, closing
        the TALES injection that previously allowed arbitrary code execution.
        """
        # Defense in depth: validate again at render time so assignments
        # created programmatically (e.g. via GenericSetup import) that bypass
        # the form field constraint are still rejected. Raises on illegal names.
        _valid_name(self.data.template)
        _valid_name(self.data.macro)
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
