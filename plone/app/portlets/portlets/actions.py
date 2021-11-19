from .. import PloneMessageFactory as _
from ..portlets import base
from Acquisition import aq_inner
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize import view as pm_view
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer


class IActionsPortlet(IPortletDataProvider):
    """A portlet that shows an action category"""

    ptitle = schema.TextLine(
        title=_("label_title", default="Title"),
        description=_("help_title", default="Displayed title of this portlet"),
        default="",
        required=False,
    )

    show_title = schema.Bool(
        title=_("label_show_title", default="Show title"),
        description=_("help_show_title", default="Show title of this portlet."),
        required=True,
        default=True,
    )

    category = schema.Choice(
        title=_("label_actions_category", default="Actions category"),
        description=_("help_actions_category", default="Select an action category"),
        required=True,
        vocabulary="plone.app.vocabularies.Actions",
    )

    show_icons = schema.Bool(
        title=_("label_show_icons", default="Show icons"),
        description=_(
            "help_show_icons",
            default="Show icons or default icon for actions without icon.",
        ),
        required=True,
        default=True,
    )

    default_icon = schema.ASCIILine(
        title=_("label_default_icon", default="Default icon"),
        description=_(
            "help_default_icon",
            default="What icon we should use for actions with no specific icons. A 16*16 pixels image.",
        ),
        required=False,
        default="action_icon.png",
    )


@implementer(IActionsPortlet)
class Assignment(base.Assignment):
    """Portlet assignment.
    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    ptitle = ""
    show_title = True
    category = ""
    show_icons = True
    default_icon = "action_icon.png"

    def __init__(
        self,
        ptitle="",
        show_title=True,
        category="",
        show_icons=True,
        default_icon="action_icon.png",
    ):
        self.ptitle = ptitle
        self.show_title = show_title
        self.category = category
        self.show_icons = show_icons
        self.default_icon = default_icon
        return

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _("Actions portlet") + ' "%s"' % (self.ptitle or self.category)


class Renderer(base.Renderer):
    """Actions portlet renderer."""

    render = ViewPageTemplateFile("actions.pt")

    @property
    def available(self):
        """Override base class"""
        return bool(self.actionLinks())

    @property
    def title(self):
        """Portlet title"""
        return self.data.ptitle

    @property
    def showTitle(self):
        """Show portlet title"""
        return self.data.show_title

    def actionLinks(self):
        """Features of action links"""
        return self.cachedLinks(
            self.data.category, self.data.default_icon, self.data.show_icons
        )

    @property
    def category(self):
        return getUtility(IIDNormalizer).normalize(self.data.category)

    @pm_view.memoize
    def cachedLinks(self, actions_category, default_icon, show_icons):
        context_state = getMultiAdapter(
            (aq_inner(self.context), self.request), name="plone_context_state"
        )
        actions = context_state.actions(actions_category)

        def render_icon(category, action_id, default):
            # We don't show icons whatever
            return None

        # Building the result as list of dicts
        result = []

        if actions_category == "portal_tabs":
            # Special case for portal_tabs (we rely on content in Plone root)
            portal_tabs_view = getMultiAdapter(
                (self.context, self.context.REQUEST), name="portal_tabs_view"
            )
            actions = portal_tabs_view.topLevelTabs(actions=actions)
            for action in actions:
                link = {
                    "id": action["id"],
                    "url": action["url"],
                    "title": action["name"],
                    "icon": render_icon(actions_category, action, default=default_icon),
                }
                result.append(link)
        else:
            if actions_category == "object_buttons":
                actions_tool = getMultiAdapter(
                    (aq_inner(self.context), self.request), name="plone_tools"
                ).actions()
                actions = actions_tool.listActionInfos(
                    object=aq_inner(self.context), categories=(actions_category,)
                )
            for action in actions:
                if not (
                    action["available"]
                    and action["visible"]
                    and action["allowed"]
                    and action["url"]
                ):
                    continue
                link = {
                    "id": action["id"],
                    "url": action["url"],
                    "title": action["title"],
                    "icon": render_icon(actions_category, action, default=default_icon),
                    "modal": action.get("modal"),
                }
                result.append(link)
        return result


class AddForm(base.AddForm):
    """Portlet add form.
    This is registered in configure.zcml. The schema attribute tells
    plone.autoform which fields to display. The create() method actually
    constructs the assignment that is being added.
    """

    schema = IActionsPortlet
    label = _("heading_add_actions_portlet", default="Add actions portlet")
    description = _(
        "help_add_actions_portlet",
        default="An action portlet displays actions from a category",
    )

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The schema attribute tells
    plone.autoform which fields to display.
    """

    schema = IActionsPortlet
