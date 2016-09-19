from five.formlib import formbase
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.formlib import form

import zope.event
import zope.lifecycleevent

from Acquisition import aq_parent, aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from plone.app.form import named_template_adapter
from plone.app.form.interfaces import IPlonePageForm
from plone.app.form.validators import null_validator

from plone.app.portlets import PloneMessageFactory as _
from plone.app.portlets.interfaces import IPortletPermissionChecker
from plone.app.portlets.browser.interfaces import IPortletAddForm
from plone.app.portlets.browser.interfaces import IPortletEditForm

# Add a named template form, which allows us to carry some extra information
# about the referer
_template = ViewPageTemplateFile('templates/portlets-pageform.pt')
portlets_named_template_adapter = named_template_adapter(_template)


class AddForm(formbase.AddFormBase):
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

    implements(IPortletAddForm, IPlonePageForm)

    form_name = _(u"Configure portlet")

    def __call__(self):
        IPortletPermissionChecker(aq_parent(aq_inner(self.context)))()
        return super(AddForm, self).__call__()

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

    @form.action(_(u"label_save", default=u"Save"), name=u'save')
    def handle_save_action(self, action, data):
        self.createAndAdd(data)

    @form.action(_(u"label_cancel", default=u"Cancel"),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''


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
        return ''

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
            url = self.context.absolute_url()
        return url + '/@@manage-portlets'

    def create(self):
        raise NotImplementedError("concrete classes must implement create()")


class EditForm(formbase.EditFormBase):
    """An edit form for portlets.
    """

    implements(IPortletEditForm, IPlonePageForm)

    form_name = _(u"Modify portlet")

    def __call__(self):
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

    @form.action(_(u"label_save", default=u"Save"),
                 condition=form.haveInputWidgets,
                 name=u'save')
    def handle_save_action(self, action, data):
        if form.applyChanges(self.context, self.form_fields, data, self.adapters):
            zope.event.notify(zope.lifecycleevent.ObjectModifiedEvent(self.context))
            self.status = "Changes saved"
        else:
            self.status = "No changes"

        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''

    @form.action(_(u"label_cancel", default=u"Cancel"),
                 validator=null_validator,
                 name=u'cancel')
    def handle_cancel_action(self, action, data):
        nextURL = self.nextURL()
        if nextURL:
            self.request.response.redirect(self.nextURL())
        return ''
