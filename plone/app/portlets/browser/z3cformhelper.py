from z3c.form import button
from z3c.form import form
from zope.component import getMultiAdapter
from zope.interface import implements
import zope.event
import zope.lifecycleevent

from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Acquisition import aq_parent, aq_inner, aq_base
from Acquisition.interfaces import IAcquirer

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.browser.interfaces import IPortletAddForm
from plone.app.portlets.browser.interfaces import IPortletEditForm
from plone.app.portlets.interfaces import IPortletPermissionChecker

from Products.statusmessages.interfaces import IStatusMessage

class AddForm(form.AddForm):
    implements(IPortletAddForm)

    template = ViewPageTemplateFile('templates/z3cform-portlets-pageform.pt')

    label = _(u"Configure portlet")

    def add(self, object):
        ob = self.context.add(object)
        self._finishedAdd = True
        return ob

    def __call__(self):
        self.request.set('disable_border', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super(AddForm, self).__call__()

    def createAndAdd(self, data):
        obj = self.create(data)

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
        return self.request.get('referer', '')

    def nextURL(self):
        urltool = getToolByName(self.context, 'portal_url')
        if self.referer and urltool.isURLInPortal(self.referer):
            return self.referer
        addview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(addview))
        try:
            url = str(getMultiAdapter((context, self.request),
                                      name=u"absolute_url"))
        except (TypeError, AttributeError):
            # At least in tests we can get a TypeError: "There isn't enough
            # context to get URL information. This is probably due to a bug in
            # setting up location information."
            url = self.context.absolute_url()
        return url + '/@@manage-portlets'

    @button.buttonAndHandler(_(u"label_save", default=u"Save"), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.createAndAdd(data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(nextURL)
        return ''


class EditForm(form.EditForm):
    """An edit form for portlets.
    """

    implements(IPortletEditForm)

    template = ViewPageTemplateFile('templates/z3cform-portlets-pageform.pt')

    label = _(u"Modify portlet")

    def __call__(self):
        self.request.set('disable_border', 1)
        self.request.set('disable_plone.leftcolumn', 1)
        self.request.set('disable_plone.rightcolumn', 1)
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super(EditForm, self).__call__()

    @property
    def referer(self):
        return self.request.get('referer', '')

    def nextURL(self):
        urltool = getToolByName(self.context, 'portal_url')
        if self.referer and urltool.isURLInPortal(self.referer):
            return self.referer
        editview = aq_parent(aq_inner(self.context))
        context = aq_parent(aq_inner(editview))
        try:
            url = str(getMultiAdapter((context, self.request),
                                      name=u"absolute_url"))
        except (TypeError, AttributeError):
            url = self.context.absolute_url()
        return url + '/@@manage-portlets'

    @button.buttonAndHandler(_(u"label_save", default=u"Save"), name='apply')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        changes = self.applyChanges(data)
        if changes:
            self.status = "Changes saved"
            IStatusMessage(self.request).addStatusMessage(_(u"Changes saved"),
                                                          "info")
        else:
            self.status = "No changes"
            IStatusMessage(self.request).addStatusMessage(_(u"No changes"),
                                                          "info")

        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    @button.buttonAndHandler(_(u"label_cancel", default=u"Cancel"),
                             name='cancel_add')
    def handleCancel(self, action):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(nextURL)
        return ''
