from .. import PloneMessageFactory as _
from ..browser.interfaces import IPortletAddForm
from ..browser.interfaces import IPortletEditForm
from ..interfaces import IPortletPermissionChecker
from Acquisition import aq_base
from Acquisition import aq_inner
from Acquisition import aq_parent
from Acquisition.interfaces import IAcquirer
from plone.autoform.form import AutoExtensibleForm
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from z3c.form import button
from z3c.form import field
from z3c.form import form
from zope.component import getMultiAdapter
from zope.interface import implementer

import zope.event
import zope.lifecycleevent


@implementer(IPortletAddForm)
class AddForm(AutoExtensibleForm, form.AddForm):
    """A base add form for portlets.

    Use this for portlet assignments that require configuration before being
    added. Assignment types that do not should use NullAddForm instead.

    Sub-classes should define create() and set the form_fields class variable.

    Notice the suble difference between AddForm and NullAddform in that the
    create template method for AddForm takes as a parameter a dict 'data':

        def create(self, data):
            return MyAssignment(data.get('foo'))

    whereas the NullAddForm has no data parameter:

        def create(self):
            return MyAssignment()
    """

    template = ViewPageTemplateFile("templates/z3cform-portlets-pageform.pt")

    label = _("Configure portlet")

    def add(self, object):
        ob = self.context.add(object)
        self._finishedAdd = True
        return ob

    def __call__(self):
        self.request.set("disable_border", 1)
        self.request.set("disable_plone.leftcolumn", 1)
        self.request.set("disable_plone.rightcolumn", 1)
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super().__call__()

    def createAndAdd(self, data):
        # Filter away data values that does not come from the 'core' schema.
        # Additional values can come from AutoExtensibleForm/FormExtender
        # schemas,and the portlet Assignment creation will fail if the
        # portlet AddForm create() method is using "Assignment(**data)"
        # instead of explicit parameters.
        # Extender values are set by form.applyChanges below, via the usual
        # z3cform adapter lookups.
        schema_keys = field.Fields(self.schema).keys()
        unextended_data = {key: data[key] for key in schema_keys if key in data}
        obj = self.create(unextended_data)

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        container = aq_inner(self.context)

        if IAcquirer.providedBy(obj):
            obj = obj.__of__(container)
        form.applyChanges(self, obj, data)
        obj = aq_base(obj)

        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(obj))
        self.add(obj)
        return obj

    @property
    def referer(self):
        return self.request.get("referer", "")

    def nextURL(self):
        urltool = getToolByName(self.context, "portal_url")
        if self.referer and urltool.isURLInPortal(self.referer):
            return self.referer
        addview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(addview))
        try:
            url = str(getMultiAdapter((context, self.request), name="absolute_url"))
        except (TypeError, AttributeError):
            # At least in tests we can get a TypeError: "There isn't enough
            # context to get URL information. This is probably due to a bug in
            # setting up location information."
            url = self.context.absolute_url()
        return url + "/@@manage-portlets"

    @button.buttonAndHandler(_("label_save", default="Save"), name="add")
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    @button.buttonAndHandler(_("label_cancel", default="Cancel"), name="cancel_add")
    def handleCancel(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(nextURL)
        return ""


class NullAddForm(BrowserView):
    """An add view that will add its content immediately, without presenting
    a form.

    You should subclass this for portlets that do not require any configuration
    before being added, and write a create() method that takes no parameters
    and returns the appropriate assignment instance.
    """

    def __call__(self):
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        ob = self.create()
        zope.event.notify(zope.lifecycleevent.ObjectCreatedEvent(ob))
        self.context.add(ob)
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ""

    @property
    def referer(self):
        return self.request.get("referer", "")

    def nextURL(self):
        urltool = getToolByName(self.context, "portal_url")
        if self.referer and urltool.isURLInPortal(self.referer):
            return self.referer
        else:
            addview = aq_parent(aq_inner(self.context))
            context = aq_parent(aq_inner(addview))
            try:
                url = str(getMultiAdapter((context, self.request), name="absolute_url"))
            except (TypeError, AttributeError):
                url = self.context.absolute_url()
            return url + "/@@manage-portlets"

    def create(self):
        raise NotImplementedError("concrete classes must implement create()")


@implementer(IPortletEditForm)
class EditForm(AutoExtensibleForm, form.EditForm):
    """An edit form for portlets."""

    template = ViewPageTemplateFile("templates/z3cform-portlets-pageform.pt")

    label = _("Modify portlet")

    def __call__(self):
        self.request.set("disable_border", 1)
        self.request.set("disable_plone.leftcolumn", 1)
        self.request.set("disable_plone.rightcolumn", 1)
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super().__call__()

    @property
    def referer(self):
        return self.request.get("referer", "")

    def nextURL(self):
        urltool = getToolByName(self.context, "portal_url")
        if self.referer and urltool.isURLInPortal(self.referer):
            return self.referer
        editview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(editview))
        try:
            url = str(getMultiAdapter((context, self.request), name="absolute_url"))
        except (TypeError, AttributeError):
            url = self.context.absolute_url()
        return url + "/@@manage-portlets"

    @button.buttonAndHandler(_("label_save", default="Save"), name="apply")
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = "Changes saved"
            IStatusMessage(self.request).addStatusMessage(_("Changes saved"), "info")
        else:
            self.status = "No changes"
            IStatusMessage(self.request).addStatusMessage(_("No changes"), "info")

        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ""

    @button.buttonAndHandler(_("label_cancel", default="Cancel"), name="cancel_add")
    def handleCancel(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(nextURL)
        return ""
