from plone.app.portlets.browser.interfaces import IPortletAddForm
from plone.app.portlets.browser.interfaces import IPortletEditForm
from plone.app.portlets.portlets import news
from plone.app.portlets.storage import PortletAssignmentMapping
from plone.app.portlets.tests.base import PortletsTestCase
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletRenderer
from plone.portlets.interfaces import IPortletType
from plone.z3cform.fieldsets.extensible import FormExtender
from plone.z3cform.fieldsets.interfaces import IFormExtender
from z3c.form import field
from zope import schema
from zope.component import adapter
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


# A sample schemaextender:


EXTENDER_PREFIX = "portletcssclass"


class IPortletCssClass(Interface):
    """Schema for portlet css class"""

    # css_class is just an example.
    # In real life a css_class implementation would be a
    # Choice field with a vocabulary, editable in a controlpanel.
    css_class = schema.TextLine(title="Portlet appearance", required=False)


class PortletCssClassFormExtender(FormExtender):
    def update(self):
        self.add(IPortletCssClass, prefix=EXTENDER_PREFIX)


@adapter(IPortletAssignment)
@implementer(IPortletCssClass)
class PortletCssClassAdapter:
    def __init__(self, context):
        # avoid recursion
        self.__dict__["context"] = context

    def __setattr__(self, attr, value):
        settings = IPortletAssignmentSettings(self.context)
        settings[attr] = value

    def __getattr__(self, attr):
        settings = IPortletAssignmentSettings(self.context)
        return settings.get(attr, None)


class TestSchemaExtender(PortletsTestCase):
    def test_addform_fields(self):
        schema_field_names = [k for k in field.Fields(news.INewsPortlet).keys()]

        # We use the news portlet as a random example of a portlet
        portlet = getUtility(IPortletType, name="portlets.News")

        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        addview = mapping.restrictedTraverse("+/" + portlet.addview)
        addview.update()
        addview_field_names = [k for k in addview.fields.keys()]

        # Our addview schema before we register our extender:
        self.assertEqual(addview_field_names, schema_field_names)

        # Register our schemaextender
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(PortletCssClassAdapter, (IPortletAssignment,))
        gsm.registerAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletAddForm),
            IFormExtender,
            "portletcssclass.extender",
        )

        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        addview = mapping.restrictedTraverse("+/" + portlet.addview)
        addview.update()
        addview_field_names = [k for k in addview.fields.keys()]

        gsm.unregisterAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletAddForm),
            IFormExtender,
            "portletcssclass.extender",
        )
        gsm.unregisterAdapter(PortletCssClassAdapter, (IPortletAssignment,))

        # Our addview schema now includes our extended schema:
        self.assertEqual(
            addview_field_names, schema_field_names + [EXTENDER_PREFIX + ".css_class"]
        )

    def test_invoke_add_form(self):
        portlet = getUtility(IPortletType, name="portlets.News")
        mapping = self.portal.restrictedTraverse("++contextportlets++plone.leftcolumn")
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)
        addview.update()
        addview.createAndAdd(
            data={"count": 5, EXTENDER_PREFIX + ".css_class": "my-class"}
        )
        portlet_assignment = mapping.values()[0]
        settings = IPortletAssignmentSettings(portlet_assignment)

        self.assertEqual(portlet_assignment.count, 5)
        # We have not extended our storage adapter, so nothing gets saved:
        self.assertIsNone(settings.get("css_class", None))

        # Register our schemaextender
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(PortletCssClassAdapter, (IPortletAssignment,))
        gsm.registerAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletAddForm),
            IFormExtender,
            "portletcssclass.extender",
        )
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse("+/" + portlet.addview)
        addview.update()
        addview.createAndAdd(
            data={"count": 5, EXTENDER_PREFIX + ".css_class": "my-class"}
        )
        portlet_assignment = mapping.values()[0]
        settings = IPortletAssignmentSettings(portlet_assignment)

        gsm.unregisterAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletAddForm),
            IFormExtender,
            "portletcssclass.extender",
        )
        gsm.unregisterAdapter(PortletCssClassAdapter, (IPortletAssignment,))

        self.assertEqual(portlet_assignment.count, 5)
        # The prefix is used for the form field, not for the stored data:
        self.assertEqual(settings.get("css_class"), "my-class")

    def test_editform_fields(self):

        schema_field_names = [k for k in field.Fields(news.INewsPortlet).keys()]

        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST
        mapping["foo"] = news.Assignment(count=5)
        editview = getMultiAdapter((mapping["foo"], request), name="edit")
        editview.update()
        editview_field_names = [k for k in editview.fields.keys()]

        # Our editview schema before we register our extender:
        self.assertEqual(editview_field_names, schema_field_names)

        # Register our schemaextender
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(PortletCssClassAdapter, (IPortletAssignment,))
        gsm.registerAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletEditForm),
            IFormExtender,
            "portletcssclass.extender",
        )

        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST
        mapping["foo"] = news.Assignment(count=5)
        editview = getMultiAdapter((mapping["foo"], request), name="edit")
        editview.update()
        editview_field_names = [k for k in editview.fields.keys()]

        gsm.unregisterAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletEditForm),
            IFormExtender,
            "portletcssclass.extender",
        )
        gsm.unregisterAdapter(PortletCssClassAdapter, (IPortletAssignment,))

        # Our editview schema now includes our extended schema:
        self.assertEqual(
            editview_field_names, schema_field_names + [EXTENDER_PREFIX + ".css_class"]
        )

    def test_invoke_edit_form(self):
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping["foo"] = news.Assignment(count=5)
        editview = getMultiAdapter((mapping["foo"], request), name="edit")
        editview.update()
        editview.applyChanges(
            data={"count": 6, EXTENDER_PREFIX + ".css_class": "my-class"}
        )
        portlet_assignment = mapping.values()[0]
        settings = IPortletAssignmentSettings(portlet_assignment)

        self.assertEqual(portlet_assignment.count, 6)
        # We have not extended our storage adapter, so nothing gets saved:
        self.assertIsNone(settings.get("css_class", None))

        # Register our schemaextender
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(PortletCssClassAdapter, (IPortletAssignment,))
        gsm.registerAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletEditForm),
            IFormExtender,
            "portletcssclass.extender",
        )
        mapping = PortletAssignmentMapping()
        request = self.folder.REQUEST

        mapping["foo"] = news.Assignment(count=5)
        editview = getMultiAdapter((mapping["foo"], request), name="edit")
        editview.update()
        editview.applyChanges(
            data={"count": 6, EXTENDER_PREFIX + ".css_class": "my-class"}
        )
        portlet_assignment = mapping.values()[0]
        settings = IPortletAssignmentSettings(portlet_assignment)

        gsm.unregisterAdapter(
            PortletCssClassFormExtender,
            (Interface, IDefaultBrowserLayer, IPortletEditForm),
            IFormExtender,
            "portletcssclass.extender",
        )
        gsm.unregisterAdapter(PortletCssClassAdapter, (IPortletAssignment,))

        self.assertEqual(portlet_assignment.count, 6)
        # The prefix is used for the form field, not for the stored data:
        self.assertEqual(settings.get("css_class"), "my-class")

    def test_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse("@@plone")
        manager = getUtility(
            IPortletManager, name="plone.leftcolumn", context=self.portal
        )
        assignment = news.Assignment(count=5)

        renderer = getMultiAdapter(
            (context, request, view, manager, assignment), IPortletRenderer
        )
        self.assertTrue(isinstance(renderer, news.Renderer))


def test_suite():
    from unittest import makeSuite
    from unittest import TestSuite

    suite = TestSuite()
    suite.addTest(makeSuite(TestSchemaExtender))
    return suite
