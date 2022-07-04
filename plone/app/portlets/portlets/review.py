from .. import PloneMessageFactory as _
from ..browser import formhelper
from ..portlets import base
from Acquisition import aq_inner
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.registry.interfaces import IRegistry
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces.controlpanel import ISiteSchema
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope import schema
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer
from zope.interface import Interface


class IReviewPortlet(IPortletDataProvider):

    no_icons = schema.Bool(
        title=_("Suppress Icons"),
        description=_("If enabled, the portlet will not show document type icons"),
        required=False,
        default=False,
    )

    thumb_scale = schema.TextLine(
        title=_("Override thumb scale"),
        description=_(
            "Enter a valid scale name"
            " (see 'Image Handling' control panel) to override"
            " (e.g. icon, tile, thumb, mini, preview, ... )."
            " Leave empty to use default (see 'Site' control panel)."
        ),
        required=False,
        default="",
    )

    no_thumbs = schema.Bool(
        title=_("Suppress thumbs"),
        description=_("If enabled, the portlet will not show thumbs."),
        required=False,
        default=False,
    )


@implementer(IReviewPortlet)
class Assignment(base.Assignment):
    no_icons = False
    thumb_scale = None
    no_thumbs = False

    def __init__(self, no_icons=False, thumb_scale=None, no_thumbs=False):
        self.no_icons = no_icons
        self.thumb_scale = thumb_scale
        self.no_thumbs = no_thumbs

    @property
    def title(self):
        return _("Review list")


class Renderer(base.Renderer):

    render = ViewPageTemplateFile("review.pt")

    title = _("box_review_list", default="Review List")

    def __init__(self, *args):
        base.Renderer.__init__(self, *args)

    @property
    def anonymous(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter(
            (context, self.request), name="plone_portal_state"
        )
        return portal_state.anonymous()

    @property
    def available(self):
        return not self.anonymous and len(self._data())

    def review_items(self):
        return self._data()

    def full_review_link(self):
        context = aq_inner(self.context)
        mtool = getToolByName(context, "portal_membership")
        # check if user is allowed to Review Portal Content here
        if mtool.checkPermission("Review portal content", context):
            return "%s/full_review_list" % context.absolute_url()
        else:
            return None

    @memoize
    def _data(self):
        if self.anonymous:
            return []
        context = aq_inner(self.context)
        workflow = getToolByName(context, "portal_workflow")

        plone_view = getMultiAdapter((context, self.request), name="plone")
        getMember = getToolByName(context, "portal_membership").getMemberById
        toLocalizedTime = plone_view.toLocalizedTime

        idnormalizer = queryUtility(IIDNormalizer)
        norm = idnormalizer.normalize
        objects = workflow.getWorklistsResults()
        items = []
        for obj in objects:
            review_state = workflow.getInfoFor(obj, "review_state")
            creator_id = obj.Creator()
            creator = getMember(creator_id)
            if creator:
                creator_name = creator.getProperty("fullname", "") or creator_id
            else:
                creator_name = creator_id
            hasImage = True if getattr(obj, "image", None) else False
            images = obj.restrictedTraverse("@@images") if hasImage else None
            items.append(
                dict(
                    path=obj.absolute_url(),
                    title=obj.pretty_title_or_id(),
                    item_class="contenttype-" + norm(obj.portal_type),
                    description=obj.Description(),
                    creator=creator_name,
                    review_state=review_state,
                    review_state_class="state-%s " % norm(review_state),
                    mod_date=toLocalizedTime(obj.ModificationDate()),
                    hasImage=hasImage,
                    images=images,
                )
            )
        return items

    @memoize
    def thumb_scale(self):
        """Use override value or read thumb_scale from registry.
        Image sizes must fit to value in allowed image sizes.
        None will suppress thumb.
        """
        if getattr(self.data, "no_thumbs", False):
            # Individual setting overrides ...
            return None
        thsize = getattr(self.data, "thumb_scale", "")
        if thsize:
            return thsize
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ISiteSchema, prefix="plone", check=False)
        thumb_scale_portlet = settings.thumb_scale_portlet
        return thumb_scale_portlet


class AddForm(formhelper.AddForm):
    schema = IReviewPortlet
    label = _("Add Review Portlet")
    description = _("This portlet displays a queue of documents awaiting " "review.")

    def create(self, data):
        return Assignment(**data)


class EditForm(formhelper.EditForm):
    schema = IReviewPortlet
    label = _("Edit Review Portlet")
    description = _("displays a queue of documents awaiting " "review.")
