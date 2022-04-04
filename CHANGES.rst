Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

5.0.0a9 (2022-04-04)
--------------------

Breaking changes:


- Remove manage-portlets.js, this is part of mockup now [MrTango] (#159)


5.0.0a8 (2022-03-23)
--------------------

New features:


- Fixes for latest z3c.form
  [petschki] (#161)


5.0.0a7 (2021-11-23)
--------------------

Breaking changes:


- Move most (hard dependency) portlet related from `plone.app.layout`:
  Dashboard, Portlet related viewlets.
  A first step towards a Portlet-as-an-Addon story.
  [jensens] (#160)


5.0.0a6 (2021-10-16)
--------------------

Bug fixes:


- Add missing i18n:translate tags
  [erral] (#158)


5.0.0a5 (2021-09-15)
--------------------

Bug fixes:


- Remove cyclic dependency with Products.CMFPlone
  [ericof] (#155)


5.0.0a4 (2021-09-15)
--------------------

Bug fixes:


- Remove cyclic dependency with Products.CMFPlone, plone.app.layouts
  [ericof] (#152)


5.0.0a3 (2021-09-01)
--------------------

Bug fixes:


- Codestyle (black/isort/pycln), Pyupgrade, plus minor manual cleanup.
  [jensens] (#151)


5.0.0a2 (2021-06-30)
--------------------

Bug fixes:


- Only allow http and https urls in RSS portlet.
  From `Products.PloneHotfix20210518 <https://plone.org/security/hotfix/20210518/blind-ssrf-via-feedparser-accessing-an-internal-url>`_.
  [maurits] (#3274)


5.0.0a1 (2021-04-20)
--------------------

Breaking changes:


- Update dashboard for Plone 6 with Bootstrap markup
  [1letter] (#144)


4.4.6 (2020-09-28)
------------------

Bug fixes:


- fixes  index error in navigation portlet caused by unknown mimetypes without
  entry in mimetype registry
  https://github.com/plone/Products.CMFPlone/issues/2882) (cmfplone-2882)
- Fixed deprecation warning for ``zope.component.interfaces.IComponentRegistry``.
  [maurits] (#3130)


4.4.5 (2020-04-20)
------------------

Bug fixes:


- Minor packaging updates. (#1)


4.4.4 (2019-12-02)
------------------

Bug fixes:


- - Remove role="navigation" from Navigation portlet.
    [ericof] (#128) (#128)
- Fix review portlet when show on the portal-root (#130)


4.4.3 (2019-10-21)
------------------

Bug fixes:


- Fix default value for label_msgid
  [erral] (#133)


4.4.2 (2019-03-21)
------------------

Bug fixes:


- Fix loading portlets with `@@render-portlet` [petschki] (#124)


4.4.1 (2019-02-08)
------------------

Bug fixes:


- a11y: Added role attribute for portalMessage [nzambello] (#119)
- Remove last traces of ZopeTestCase. [gforcada] (#121)


4.4.0 (2018-10-31)
------------------

New features:

- Adapt tests to `Products.GenericSetup >= 2.0` thus requiring at least that
  version.
  [icemac]

- Add python 3 compatability
  [pbauer, ale-rt, jensens]

Bug fixes:

- Fix browser tests to work with merged plone.login.
  [jensens]

- Imports are Python3 compatible
  [ale-rt]

- base.Renderer no longer mixes in Acquisition.Explicit,
  so attributes of the renderer will no longer be wrapped.
  [davisagli]

- Catch NotFound while trying to traverse to portlet add views
  to check permission.
  [davisagli]

- Test against plone.app.contenttypes instead of ATContentTypes.
  [davisagli]

- Portlet add and edit forms already extend AutoExtensibleForm from
  plone.autoform. But some portlet
  addforms fail on creating the Assignment, if there is a FormExtender
  for the form, and the addform uses `Assignment(**data)` for creation
  instead of explicit parameters. Fix this by filtering
  away data values that does not come from the 'core' schema.
  [sunew]

- Remove an outdated test and some cleanup.
  [jensens]


4.3.1 (2017-08-07)
------------------

New features:

- navigation-, news-, recent-,review-portlets: add options to supress icons,
  read thumb_scale from registry plus  option to override thumb_scale individually
  or suppress thumbs.
  Replace paper clip (fontello icon) with mimetype icon
  from mimetype registry for files
  https://github.com/plone/Products.CMFPlone/issues/1734
  [fgrcon]

Bug fixes:

- removed unittest2 dependency
  [kakshay21]


4.3.0 (2017-03-26)
------------------

New features:

- Make use of plone.namedfile's tag() function to generate image tags.
  Part of plip 1483.
  [didrix]


4.2.3 (2017-02-12)
------------------

Bug fixes:

- fixed css-classes for thumb scales ...
  https://github.com/plone/Products.CMFPlone/issues/2077
  [fgrcon]

- Fix regression where navigation portlet ignored unlimited setting for
  *Navigation tree depth* setting
  [datakurre]

- Make sure, that ``utils.assignment_mapping_from_key`` traverses only to non-unicode paths.
  OFS.traversable doesn't accept unicode paths.
  [thet]


4.2.2 (2016-11-18)
------------------

Bug fixes:

- Put ellipsis out of the title_switch_portlet_managers (Other portlet
  managers) message.
  [vincentfretin]


4.2.1 (2016-10-03)
------------------

Bug fixes:

- Added ``referer`` property to ``PortletAdding`` view.  Now all views
  like this have it.  [maurits]

- Apply security hotfix 20160830 for redirects.  [maurits]

- Add coding header on python files.
  [gforcada]

4.2 (2016-08-12)
----------------

New features:

- Add category as CSS class to actions portlet for easier styling
  [tomgross]

- Upgrade news portlet to use the new select widget;
  Add dependency on plone.app.z3cform
  [datakurre]

- Tracebak info on importing ``portlets.xml`` to show better error location in the xml
  [SyZn]

Bug fixes:

- Use zope.interface decorator.
  [gforcada]

- Change ``plone-manage-portlets`` to use Patternslib base pattern ``pat-base``.
  [thet]

- Use absolute source URL in navigation portlet's thumbnails
  [davilima6]


4.1.2 (2016-06-07)
------------------

Bug fixes:

- Fixed missing pat-livesearch on search portlet
  [agitator]

- Remove Plone 3 compatibility code
  [tomgross]


4.1.1 (2016-05-26)
------------------

Bug fixes:

- Improved documentation about ``portlets.xml``.  This is
  automatically included in
  http://docs.plone.org/develop/addons/components/genericsetup.html
  [maurits]


4.1.0 (2016-05-15)
------------------

New:

- Add jumplist to provide quick access across portlet managers
  [davilima6]


4.0.0 (2016-03-31)
------------------

Incompatibilities:

- Changed these ``section`` elements to ``div`` elements:
  ``.portletHeader``, ``.portletContent``.  Changed these ``section``
  elements to ``aside`` elements: ``.portletActions``,
  ``.portletLanguage``, ``.portletLogin``, ``.portletNavigationTree``,
  ``.portletNews``, ``.portletRecent``, ``.portletWorkflowReview``,
  ``.portletRss``, ``.portletSearch``.  This might affect your custom
  styling or javascript or robot tests.  [maurits]

Fixes:

- Fixed html validation:
  - section lacks heading
  - bad value 'menu' for attribute role on element section
  - bad value 'section' for attribute role on element section
  - attribute alt not allowed on element input at this point
  - bad value menu for attribute role on element section.
  [maurits]


3.1.3 (2015-11-25)
------------------

Fixes:

- Added authenticator token to group portlet links.
  [vangheem]

- Fixed links in RSS portlets when using special characters.
  [Gagaro]



3.1.2 (2015-09-27)
------------------

- Log exceptions while parsing rss feeds. Get logged as info since
  this often caused by factor out of control of site owners and
  because the problem is handled in the UI
  [do3cc]

- Remove hard coded 10 minute delay if retrieving a feed failed once.
  Either you don't need your feeds ultra fast, then you can create
  a longer time, or you need them fast and don't want this hidden delayq
  [do3cc]

- Add caching functionality from feedparser.
  [do3cc]

- Use ``is_default_page`` instead of ``check_default_page_via_view``.
  [fulv]


3.1.1 (2015-09-20)
------------------

- Remove global settings for navigation tree's top_level,
  current_folder_only
  [esteele]

- Prevent values lower than 1 in number of items.
  [pbauer]

- Resolve deprecation warning for isDefaultPage.
  [fulv]


3.1 (2015-09-14)
----------------

- Fix broken link in manage-content-type-portlets.
  https://github.com/plone/Products.CMFPlone/issues/959
  [pbauer]


3.0.10 (2015-09-11)
-------------------

- Fix extra portletFooter on account of missing tal statement within news.pt
  [ichim-david]

- If 'currentFolderOnly', navigation portlet header link should go to current
  folder, not to sitemap
  [ebrehault]


3.0.9 (2015-09-09)
------------------

- Fix single portlet manager management to not show other portlet
  manager that are rendered on the same page. This fixes the odd
  case where the footer portlets were editable on a page where
  only the left or right side portlets should be editable
  [vangheem]


3.0.8 (2015-09-07)
------------------

- Remove usage of global defines in classic portlet.
  [esteele]

- Use registry lookup to get filter_on_workflow and
  workflow_states_to_show settings.
  [esteele]


3.0.7 (2015-07-18)
------------------

- Change role to be a valid one.
  [polyester]


3.0.6 (2015-06-05)
------------------

- Convert manage-portlets.js into a pattern and make improvements on
  using the manage portlets infrastructure
  [vangheem]

- Remove CMFDefault dependency
  [tomgross]


3.0.5 (2015-05-12)
------------------

- Supress a ZopeTestCase warning.
  This fixes https://github.com/plone/Products.CMFPlone/issues/501
  [gforcada]


3.0.4 (2015-05-04)
------------------

- Fix html markup in review portlet.
  [vincentfretin]

- Fix the link from `@@topbar-manage-portlets` to container's portlets.
  This fixes https://github.com/plone/Products.CMFPlone/issues/423
  [davisagli]

- pat-modal pattern has been renamed to pat-plone-modal
  [jcbrand]


3.0.3 (2015-03-13)
------------------

- Read ``use_email_as_login`` setting from the registry instead of portal
  properties (see https://github.com/plone/Products.CMFPlone/issues/216).
  [jcerjak]

- Fix missing definitions of ``plone_view``. Fixes the recent portlet.
  [thet]

- Use plone_layout for getIcon.
  [pbauer]


3.0.2 (2014-10-23)
------------------

- Abstract the search form and livesearch action URLs making it easier to
  extend the search portlet with custom views or other actions.
  [rpatterson]

- Remove test dependency on plone.app.event. Fix ``convert_legacy_portlets``
  method in utils module to use correct Assignment classes.
  [thet]

- Integration of the new markup update and CSS for both Plone and Barceloneta
  theme. This is the work done in the GSOC Barceloneta theme project.
  [albertcasado, sneridagh]

- Update <div id="content"> in all templates with <article id="content">
  [albertcasado]


3.0.1 (2014-04-16)
------------------

- Transfered pbauer's fix of #32 'removing group-portlets' of 2.4.x-branch to
  master. Also Tansfered changelogs of version 2.4.4 to 2.4.8.
  [ida27]


3.0 (2014-04-05)
----------------

- Avoid storing portlet assignment mapping in the database until
  an assignment is actually added.
  [davisagli]

- Fix auto csrf protection integration.
  [vangheem]

- Use z3c.form for portlet forms.
  [bosim, davisagli]

- Store navigation portlet root setting as a UID rather than a path.
  [davisagli]


2.5.0 (2014-03-02)
------------------

- In actions portlet, include modal pattern options if specified
  as an action property.
  [davisagli]

- Fix empty img in actions portlet.
  [davisagli]

- Add actions portlet.
  [giacomos]

- Replace DL's etc. in portlets.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink]

- Remove DL's from portal message in templates.
  https://github.com/plone/Products.CMFPlone/issues/153
  [khink]

- Don't break if portal_factory is missing.
  [davisagli]

- Don't show the ``New user?`` link in the Login portlet if there isn't
  a register URL available from portal_actions.
  [davidjb]

- Fix navigation root of portlets when root field is unicode.
  This is the case when portlet is imported with generic setup.
  [thomasdesvenain]


2.5a1 (2013-10-05)
------------------

- Merge in changes from plone.app.event. portlets.Calendar and portlets.Events
  are moved to plone.app.event, while here are still BBB imports from there.
  [thet]

- Acquisition-wrap portlet assignments retrieved from storage.
  [davisagli]

- fix z3cform support - add status messages when redirecting
  [sunew / tmog]

- fix z3cform support - respect referer
  [tmog / sunew]

- fix z3cform support - fix for vocabularies, lifted from
  p.dexterity addForm.
  [tmog / sunew]

- Don't require a macro for classic portlets - rendering a browser view doesn't
  need one.
  [danjacka]

- Change class prefix for the top node from "section-" to "nav-section-"
  to avoid clash with the body tag.
  [kleist]


2.4.8 (2014-01-27)
------------------

- Fixed navigation portlet when navigation root was None.
  [thomasdesvenain]


2.4.7 (2013-12-07)
------------------

- Fix navigation root of portlets when root field is unicode. This is the case when portlet is imported with generic setup.
  [thomasdesvenain]

- Don't show the New user? link in the Login portlet if there isn't a register URL available from portal_actions.
  [davidjb]


2.4.6 (2013-09-14)
------------------

- Use relative links for calender next and prev buttons since caching can cause these things to change the current page the user is viewing
  [vangheem]
- Fix the removing of Group- and Typeportlets https://dev.plone.org/ticket/13659
  [pbauer]


2.4.5 (2013-08-13)
------------------

- Acquisition-wrap portlet assignments retrieved from storage.
  [davisagli]

- Fixed calendar portlet from "Event" to portal_calendar types
  [dr460neye]

- Fixed events.py to all portal_calendar types.
  [dr460neye]

- Fixed event portlet. Static Type removed and changed to portal_calendar type.
  [dr460neye]


2.4.4 (2013-05-23)
------------------

- Don't require a macro for classic portlets - rendering a browser view doesn't need one.
  [danjacka]


2.4.3 (2013-04-06)
------------------

- Fixed redirection after changing a portlet.
  [maurits]

- Fixed portal_calendar single type "links" in the calendar template.
  [dr460neye]


2.4.2 (2013-03-05)
------------------

- Make it possible to delete broken portlet assignment.
  [vipod]

- Make sure a portlet name is not a unicode string. This prevents problems when
  trying to use a portlet name in joined strings.
  [wichert]


2.4.1 (2013-01-01)
------------------

- Navigation portlet: Add "section-XXX" class for the top node, useful for
  background colors/images.
  [kleist]

- Don't break if a feed does not have an "rel=alternate type=html" link. It is
  possible for a valid Atom feed to omit a <link rel="alternate" type="html"
  href="http://server.com"/> element which is available through the feedparser
  object as a feed.link attribute. If the feed does not have this element then
  the RSS portlet will throw an AttributeError which will propagate to the page
  preventing the original page from rendering.  This changeset adds support for
  such feeds.
  [dokai]


2.4.0 (2012-10-16)
------------------

- We can delete a portlet which product has been removed.
  Manage portlets page is not broken when an inherited portlet is broken.
  [thomasdesvenain]

- Add ability to render only single portlet code with view.
  Code basically copied from plone.app.kss
  [vangheem]

- Remove kss
  [vangheem]

- Allow for the root content item icon in the navigation portlet to be
  displayed with CSS or an img tag.
  [danjacka]


2.3.5 (2012-09-28)
------------------

- Fix inheritance hierarchy of IPortletForm to reflect usage in z3cformhelper.
  [elro]


2.3.4 (2012-09-28)
------------------

- Tweak z3c.form add/edit forms to disable edit bar and columns.
  [elro]


2.3.3 (2012-09-27)
------------------

- Portlets are now registered for IDefaultPortletManager by default to allow
  for easier creation of custom portlet managers with restricted portlets.
  [elro]


2.3.2 (2012-09-26)
------------------

- Fix ManagePortletsViewlet to work with KSS.
  [elro]

- Fix ManagePortletsViewlet to work with Plone 4+.
  [elro]

- Fix 'This portlet display a'.
  [danjacka]

- reverted change: refactory nested tal:conditions in
  ``navigation_recurse.pt``, merged into one tal:condition in ul tag.
  [maartenkling]

- Add contenttype class to the a tag, like navigation
  [maartenkling]

- Don't break TinyMCE on editing parent-portlets (fixes
  http://dev.plone.org/ticket/12899)
  [pbauer]

- Inside Review portlet display footer link only to Reviewers.
  Closes ticket https://dev.plone.org/ticket/6629
  [vipod]

- Use ``type`` instead of ``makeClass`` for Zope 4 compatibility.
  [elro]

- Add safety check for portletHeader links [davilima6]


2.3.1 (2012-08-29)
------------------

- Fix packaging error.
  [esteele]


2.3 (2012-08-29)
----------------

- Calendar portlet links to @@search (plone.app.search) view instead of
  deprecated search.pt.
  [seanupton]

- When navigation portlet has an explicit custom root set, clicking the portlet
  heading goes to this content item instead of the global sitemap.  (Plone
  doesn't support section sitemaps)
  [miohtama]

- If navigation portlet bottom level is set to a negative value, don't query
  navigation items at all, only display portlet header and footer
  [miohtama]

- In the portlet management interface display the assigned name of the
  navigation portlet if it has one
  [miohtama]

- Calendar portlet search URLs whitelist only Event portal_type in the
  querystring, prevents non-event types from accidentally being
  included in calendar results.
  [seanupton]

- Navigation portlet template renders a non-site navigation root content
  item with its apporpriate content icon, reserving the Plone site icon
  CSS sprite for default use by a site only.
  [seanupton]

- portlets/login.py, portlets/navigation.py:
  Don't use list as default parameter value.
  [kleist]

- refactory nested tal:conditions in ``navigation_recurse.pt``, merged into
  one tal:condition in ul tag.
  [saily]

- Add link to @@manage-portlets to go up to the parent folder staying in
  manage-portlets viewlet
  [toutpt]


2.3a1 (2012-06-29)
------------------

- Make it possible to create portlets using z3c.form.
  [ggozad]


2.2.6 (unreleased)
------------------

- Remove hard dependency on Archetypes.
  [davisagli]

- accessibility improvements for screen readers regarding "more" links, see
  https://dev.plone.org/ticket/11982
  [rmattb, applied by polyester]


2.2.5 (2012-05-07)
------------------

- Changed the permission for members to be able to add portlets
  to their dashboards. ( https://dev.plone.org/ticket/11174 )
  [credits to buchi and jstegle, applied and tests by frapell]


2.2.4 (2012-04-15)
------------------

- Prevent buggy RSS feed to break page display.
  [patch by dieter, applied by kleist]

- Fix inherited local portlets for objects allowing locally-assigned
  portlets which are contained by an object that does not.
  [mitchellrj]


2.2.3 (2011-11-24)
------------------

- Do not display 'Manage portlets' when using portal_factory.
  https://dev.plone.org/ticket/12376
  [runyaga]

- Fixed the two high priority scenarios (global sections viewlet and nav
  portlet) of http://dev.plone.org/ticket/11189.
  [fulv]

- Reverted commit 5cb41ffea to fix #12279 and added a test for it.
  [zupo, jcerjak]


2.2.2 (2011-10-17)
------------------

- Fixed issue where the events, news and recent portlet would fail
  with a setting of no items (zero) shown due to a catalog sorting
  assertion.
  [malthe]

- Avoid empty <ul> tag in navigation_recurse.pt if bottomLevel is set.
  [gaudenzius]

- Enable possibility to delete portlets with missing implementation
  [do3cc]

- Replace use of deprecated skin template prefs_group_details with
  @@usergroup-groupdetails.
  [stefan]


2.2.1 - 2011-08-08
------------------
- Imporove tests readability. Merged from branches/2.1
  [gotcha]

- 'placeholder' attribute for the search portlet's field instead of the custom
  JS handling of the same functionality.
  [spliter]


2.2 - 2011-07-19
----------------

- Updated 'Advanced Search' link and form's action of the search portlet to
  link to updated search results view at @@search.
  [spliter]


2.1.5 - 2011-06-19
------------------

- Fixed i18n regression caused by the pep8 cleanup.
  [vincentfretin]


2.1.4 - 2011-05-11
------------------

- Fixed navigation portlet when include top activated
  and no navigation root selected (bug appears behind apache).
  [thomasdesvenain]

- Sort exported portlet types and portlet manager registrations by name to
  avoid intermittent test failures.
  [davisagli]


2.1.3 - 2011-04-21
------------------

- Let the portlets import step depend on the content import step
  again.  Refs http://dev.plone.org/plone/ticket/8350
  [maurits]

- Add test ``testINavigationRootWithRelativeRootSet``.
  Cfr. http://dev.plone.org/plone/ticket/8787
  [anthonygerrard, WouterVH]

- Add MANIFEST.in.
  [WouterVH]

- Fix circular dependency in import steps.
  This partially fixes http://dev.plone.org/plone/ticket/8350
  [kiorky]


2.1.2 - 2011-02-10
------------------

- Enable managing portlets of default pages.
  This fixes http://dev.plone.org/plone/ticket/10672
  [fRiSi]

- Be more graceful, when user doesn't belong to groups - e.g. when user is
  defined in non-PAS based top-level acl_users folder.
  Fixes http://dev.plone.org/plone/ticket/9929
  [thet]


2.1.1 - 2011-01-03
------------------

- Depend on ``Products.CMFPlone`` instead of ``Plone``.
  [elro]


2.0.2 - 2010-12-23
------------------

- Recover from parse error on ``updated`` date.
  [malthe]

- Display full creator name in review portlet.
  [thomasdesvenain]

- Do not display portlets add select list if it is empty.
  [thomasdesvenain]

- Recent items and Review list portlets title is got by a title attribute
  on the renderer.
  [thomasdesvenain]

- Fix the IPortletDirective schema's default edit_permission to match
  the default that is actually supplied by the directive's implementation.
  [davisagli]

- Fix RSS portlet edge case. The feedparser may not have a 'bozo' attribute
  if libxml2 is not present on the system.
  [stefan]

- Fix #11409: use the TTW customized view name if any.
  [kiorky]


2.0.1 - 2010-09-09
------------------

- Proper checkup for navigation portlet's title - we don't show it
  unless the title is explicitly specified.
  [spliter]


2.0 - 2010-07-18
----------------

- Update license to GPL version 2 only.
  [hannosch]


2.0b11 - 2010-06-13
-------------------

- Stop abusing traditional layers to do database changes.
  [hannosch]

- Avoid deprecation warnings under Zope 2.13.
  [hannosch]

- Avoid using the deprecated five:implements directive.
  [hannosch]

- Updated to use five.formlib.
  [hannosch]


2.0b10 - 2010-06-03
-------------------

- Fixed an issue with the portlet calendar cache not being invalidated
  when adding a new event in the last day of the month. This closes
  http://dev.plone.org/plone/ticket/10598.
  [deo]

- Moved condition for navigation portlet's title to DT element. We
  don't need empty DT in case title is not provided for the portlet.
  [spliter]

- Fix GS export of portlets assignments
  when property is a tuple or a list
  http://dev.plone.org/plone/ticket/10530
  [macadames]

- Remove deprecated use of tabindex.
  [edegoute]

- Fix regressions in date handling in events portlet.
  Fixes http://dev.plone.org/plone/ticket/10506.
  [davisagli]


2.0b9 - 2010-05-01
------------------

- Add notice (and link to container) when managing the portlets of the default
  item in a container. This fixes http://dev.plone.org/plone/ticket/10456
  [dunlapm]

- Fix portlets not showing for "normal" users.
  Fixes http://dev.plone.org/plone/ticket/10461
  [zupo, dunlapm]

- Not showing inherited portlets that are blocked at an upper level.
  Fixes http://dev.plone.org/plone/ticket/10426
  [igbun]

- Improve styling of date + location in news + event portlets
  [jonstahl]

- Use unicode up/down arrows in the @@manage-portlet view.
  [esteele]

- Make the navigation portlet hide the portal header if title is left blank.
  Refs http://dev.plone.org/plone/ticket/10432
  [esteele]

- Fix the calendar portlet to generate links that work on non-default views
  when logged out. Closes http://dev.plone.org/plone/ticket/10045.
  [davisagli]


2.0b8 - 2010-04-10
------------------

- Fix the edit manager template to include the manager id again, so that
  KSS can update the manager when actions take place. Closes
  http://dev.plone.org/plone/ticket/10404.
  [davisagli]

- Catch KeyError in EditPortletManagerRenderer. Now the manage-portlets
  doesn't break on invalid portlets any longer.
  [tom_gross]


2.0b7 - 2010-04-07
------------------

- Convert the root (site) node to use CSS sprites in the navigation portlet.
  [limi]

- Use CSS sprites instead of individual images for core content types in the
  navigation portlet.
  [limi]

- Add test coverage for empty type icons in the navigation portlet.
  [rossp]


2.0b6 - 2010-03-05
------------------

- Added navtree-section-class to li. This closes
  http://dev.plone.org/plone/ticket/10247.
  [hpeteragitator]

- Remove a label for attribute that points to nothing, invalid HTML.
  [rossp]

- Fix invalid HTML by moving the xmlns declarations into a tag that will
  be omitted by TAL.
  [rossp]

- Avoid ConstraintNotSatisfied error when GS-importing the default
  navigation portlet. Fixes http://dev.plone.org/plone/ticket/10232.
  [WouterVH, hannosch]


2.0b5 - 2010-02-18
------------------

- Updated portlets-pageform.pt to disable columns via REQUEST variable.
  [spliter]


2.0b4 - 2010-02-17
------------------

- Updated @@manage-group-dashboard to the recent markup conventions.
  References http://dev.plone.org/plone/ticket/9981 and
  http://dev.plone.org/plone/ticket/10231.
  [spliter]

- Updated manage-dashboard.pt and manage-group.pt to use the recent markup
  conventions.
  References http://dev.plone.org/old/plone/ticket/9981.
  [spliter]

- Removing redundant .documentContent markup.
  This refs http://dev.plone.org/plone/ticket/10231.
  [limi]

- Changed "manage portlets"-related templates to use markup according
  to the recent conventions.
  References http://dev.plone.org/plone/ticket/9981.
  [spliter]

- Change language portlet to call update() on LanguageSelector.
  [elro]

- Navtree item_icon must be accessed nocall: for later item_icon/html_tag.
  [elro]


2.0b3 - 2010-01-28
------------------
- Change group portlets and group dashboard links to point to the new
  @@usergroup-groupmembership view.
  [esteele]


2.0b2 - 2010-01-25
------------------

- Don't create persistent objects during module import -- it breaks test cases
  that are sandboxed into different ZODBs and import this module (leads to
  ConnectionStateErrors).
  [davisagli]

- Rework page templates for group prefs pages so that they match the rest of our
  prefs pages. Add the group dashboard link to other group prefs pages. Closes
  http://dev.plone.org/plone/ticket/9732.
  [esteele]

- Merged r30179 from branches/1.2 (this is the only fix since 1.2 that was
  missing in trunk): Some XHTML fixes to be also XHTML Strict compliant. See
  http://dev.plone.org/plone/ticket/4379 (fix by keul).
  [maurits]

- Merge r30771 from branches/1.2: Support for portal-relative paths in
  portlets.xml keys. Fixes http://dev.plone.org/plone/ticket/9764.
  [maurits]


2.0b1 - 2010-01-03
------------------

- Fixed edge-case in portlet import handler when using the extend attribute.
  [hannosch]

- Removed unhelpful log messages which cluttered the log during upgrades.
  [hannosch]


2.0a4 - 2009-12-27
------------------

- Adjusted tests to fixed IIDNormalizer semantics.
  [hannosch]

- Added missing package dependencies.
  [hannosch]


2.0a3 - 2009-12-21
------------------

- Fix XML validation for RSS portlets
  [matthewwilkes]

- Support local navigation root (INavigationRoot) for the previous
  events link in events portlet.
  Fixes http://dev.plone.org/plone/ticket/9246
  http://dev.plone.org/plone/ticket/9668
  [pelle]


2.0a2 - 2009-12-02
------------------

- Point to users to @@register instead of @@join_form.
  [esteele]

- Fix the rendering of classic portlets.
  [davisagli]

- Remove the BBB code for the old style for= attributes on import of
  portlets pre-3.1.  This was deprecated for 4.0, it now raises an error.
  [matthewwilkes]


2.0a1 - 2009-11-15
------------------

- Don't include <q> tag in title_manage_contextual_portlets message.
  [vincentfretin]

- Various cleanups, use our own message factory to lighten the dependency on
  the Plone distribution.
  [hannosch]

- Added translations for Show/Hide labels in @@manage-portlets view:
  label_show_item and label_hide_item. These msgids are shared with
  @@manage-viewlets view to show/hide viewlets. This closes
  http://dev.plone.org/plone/ticket/9733
  [naro]

- Introduced a new msgid title_edit_dashboard_group to translate
  "Edit Dashboard Portlets for $group". title_edit_dashboard msgid
  was used twice for different messages.
  [vincentfretin]

- Optimize some portlets to avoid unnecessary instructions in their
  ``__init__`` or available methods.
  [hannosch]

- Optimized join_action in the login portlet.
  [hannosch]

- Added support for showing/hiding of all portlets (PLIP 9286).
  [igbun]

- Add support for viewing blocked portlets in the management interface (PLIP
  9285)
  [igbun]

- Login portlet: when use_email_as_login is true, make the label 'E-mail'
  instead of 'Login Name', as per plip 9214 (Plone 4). Should still work in
  earlier Plone versions as well. Refs http://dev.plone.org/plone/ticket/9214.
  [maurits]

- Added support for group dashboards.
  [optilude]

- Removed last zope.app dependencies.
  [hannosch]

- Specified package dependencies.
  [hannosch]


1.2.1 - unreleased
------------------

- RSS portlet: accept the feedparser.CharacterEncodingOverride
  exception when parsing the feed as it is just a warning: the parsed
  entries will be there.
  [maurits]

- Added missing space to tooltip in the calendar portlet.
  Fixes http://dev.plone.org/plone/ticket/9047
  [lzdych]

- Navigation(s) some time disappeared when dealing with multiple navigations
  pointing to roots with common starting ids like: "abc", "abcde", "abcdefg".
  Thanks to keul for patch.
  Fixes http://dev.plone.org/plone/ticket/9405
  [pelle]

- Fixed base.Assignment - typo
  Fixes http://dev.plone.org/plone/ticket/9350
  [naro]

- Support for portal-relative paths in portlets.xml keys.
  Fixes http://dev.plone.org/plone/ticket/9437
  [naro]

- Some XHTML fixes to be also XHTML Strict compliant.
  See http://dev.plone.org/plone/ticket/4379
  [keul]


1.2 - July 13, 2009
-------------------

- Fix ComponentLookupError on portlet management screen for special use cases
  such as collective.portletpage, where not all content have the same
  managers.
  [optilude]

- Template cleanup: add missing xmlns declarations and fix invalid markup.
  [wichert]


1.2rc3 - April 8, 2009
----------------------

- Correct import error in editmanager.py.
  [optilude]

- Correct case in the feedparser dependency.
  [wichert]


1.2rc1 - March 27, 2009
-----------------------

- Added a permission check to portlets' add view.
  Fixes http://dev.plone.org/plone/ticket/8510
  [optilude]


1.2b1 - March 7, 2009
---------------------

- Fixed the various portlets to no longer use portal_url, but use the
  navigation_root_url from the plone_portal_state view. Changed the
  manage-dashboard view to be available on an INavigationRoot.
  This implements http://plone.org/products/plone/roadmap/234
  [calvinhp]

- Removed portlets/feedparser.py.  Added FeedParser as external
  requirement in setup.py instead of shipping with it.
  (This is Plip 197: http://plone.org/products/plone/roadmap/197)
  [maurits]

- Added title option to the RSS portlet.
  [davisagli]

- Clean-up unnecessary variable declarations within navigation_recurse.pt.
  Let the default view on the Link type decide what's best
  [andrewb]


1.1.7 (2011-05-19)
------------------

- Fixed exportimport to support xml CDATA, thanks to lucie
  [calvinhp]


1.1.6 - 2009-03-07
------------------

- Fixed new portlet template footer so it will validate, fixes
  http://dev.plone.org/plone/ticket/8769 thanks to bandigarf
  [calvinhp]

- Made the test independent of default content created in a site. This
  allows them to pass in both Plone 3.x and 4.x.
  [hannosch]

- Added inherited portlets to manage view. This implements
  http://dev.plone.org/plone/ticket/8426.
  [malthe]

- Modified a macro call in portlets-pageform.pt for forwards
  compatibility with Zope 2.12.
  [davisagli]

- Fixed SyntaxErrors in test_cache and test_configuration.
  [hannosch]

- Fixed Review List template that was making a bad call to
  pretty_title_or_id. This closes http://dev.plone.org/plone/ticket/8401.
  [dunlapm]


1.1.5 (2008-08-18)
------------------

- Refactored the review portlet a bit and added the review state dependent
  color coding to it. This closes http://dev.plone.org/plone/ticket/6957.
  [hannosch]

- Sort the addable portlets in the management screen by their title.
  This closes http://dev.plone.org/plone/ticket/8227.
  [hannosch]

- Disabled two tests for a not yet implemented feature regarding better
  i18n support.
  [hannosch]


1.1.3 (2008-07-07)
------------------

- Fix an accidental bug I introduced earlier: restore portletBottomLeft
  and portletBottomLeft spans in the news portlets with a more-news
  link.
  [wichert]


1.1.2 (2008-06-01)
------------------

- Fixed i18n markup.
  Fixes http://dev.plone.org/plone/ticket/7068#comment:4
  [naro]

- The portletNavigationTree class was used for both the dl and the top
  ul. This makes things inconsistent since other levels in the tree
  used a navTree class for the ul, and uses the same class for two
  semantically very different items. Fixed by using navTree for the top
  ul as well.
  [wichert]


1.1.0 (2008-04-20)
------------------

- Added test for #7942. The fix is in plone.app.layout.
  [optilude]

- Fixed #8025 so that the named feeds now work to. Changed the package to
  use a different field.
  [mrtopf]

- ViewPageTemplate is meant to be used as a class variable and only
  works as instance variable by accident in current Zope. This fixes
  errors in Philipp and Hanno's aq refactor branch of Zope2.
  [wichert]

- Add a test to demonstrate #6100 and #7860. This is fixed in
  plone.portlets already.
  [optilude]

- Use the new GenericSetup.components blacklist feature when available.
  This gives our exportimport code full control over all components
  providing either IPortletType, IPortletManager or
  IPortletManagerRenderer. This fixes
  http://dev.plone.org/plone/ticket/7149.
  [hannosch]

- Fix invalid leading space in all 'Up to Site Setup' links.
  [wichert]

- Added tests for the (not yet implemented) i18n markup support in
  portlets.xml.
  [hannosch]

- Added missing i18n markup to portlets.xml.
  [hannosch]

- label_group_members was used twice.  Renamed the second one to
  label_group_portlets (which is in plone.pot already).
  [maurits]

- Removed last remains of caching for the navigation portlet.
  This closes http://dev.plone.org/plone/ticket/7726.
  [hannosch]

- Added first day of week to calendar portlet cache key.
  [hannosch]

- Added option to purge all assignments specified by category and key.
  [fschulze]

- Added option to remove individual portal managers and purge global
  portlet manager assignments as well as assignments to the site root
  with GS profiles.
  [fschulze]

- Added option to purge portlet configuration in extension profiles.
  [fschulze]


1.1.0a1 (2008-03-09)
--------------------

- Fixed bug that caused includeTop not to be set when a navtree portlet
  was first added.
  http://dev.plone.org/plone/ticket/7798.
  [optilude]

- Made the language portlet's 'available' property work properly, avoiding
  ugly blank columns.
  [optilude]

- Made sure the manage portlets div is not shown to anonymous users.
  http://dev.plone.org/plone/ticket/7911.
  [optilude]

- Optimised the news portlet template.
  http://dev.plone.org/plone/ticket/7760
  [optilude]

- Made the <plone:portletRenderer /> directive more forgiving.
  http://dev.plone.org/plone/ticket/7703
  [optilude]

- Fixed a silly bug in the search portlet.
  http://dev.plone.org/plone/ticket/7388.
  [optilude]

- Made it possible to remove single portlet assignments by using the
  "remove" attribute.
  [fschulze]

- PLIP203: Add the ability to export and import portlet assignments and
  blacklisting.
  [optilude]

- PLIPs 205 and 218: Allow registering portlet types to multiple portlet
  manager interfaces, require portlet types to be explicitly registered
  for portlet manager interfaces, enable modifying registrations through
  GenericSetup, and restrict most default Plone portlet types to left/
  right/dashboard columns.
  [sirgarr]

- PLIP207: Allow custom portlet managers, i.e., allow specifying an
  alternative portlet manager class through GenericSetup.
  [sirgarr]


1.0.7 (UNRELEASED)
------------------

- Allow non-ASCII object paths while calculating cache key for
  portlets.  This fixes http://dev.plone.org/plone/ticket/7086
  [nouri]

- Make the language portlet handle languages without a native name
  correctly.
  [wichert]

- Do not link to news_listing from the news portlet: that template has
  been removed from Plone. This fixes
  http://dev.plone.org/plone/ticket/7872
  [wichert]


1.0.6
-----

- Sort the languages in the language portlet using their native name.
  [wichert]

- Fixed None value in query_string in calendar portlet. This closes
  http://dev.plone.org/plone/ticket/7331.
  [hannosch]

- Fixed logic error in getRootPath in the last change.
  [hannosch]

- Only show the language portlet if more than one language is available.
  This brings it in sync with the language selection viewlet.
  [wichert]

- Fix missing variable on the language portlet renderer. This fixes
  NuPlone which relies on the language selector portlet.
  [wichert]

- Fixed undefined variable name introduced in the last change.
  [hannosch]

- Correct getRootPath to not add a trailing / to paths if there
  are no context subelements. This was breaking webcouturier.dropdownmenu
  in situations where one of the sections was a navigation root.
  [wichert]


1.0.5
-----

- Made absolute_url() work properly on the custom adding views. This is
  necessary for the <base /> URL to be set correctly.
  [optilude]

- Handle RSS feed entries which do not have an update timestamp correctly.
  This fixes http://dev.plone.org/plone/ticket/7515
  [wichert]

- Provide proper 'id' implementations for assignment mappings and
  assignments. This makes absolute_url() work properly.
  [optilude]


1.0.2
-----

- Always try to refresh the RSS feed when rendering it instead of waiting
  for KSS to do trigger an updated. This is needed for the very common
  situation where most users are anonymous and the the feeds would expire
  (or never be loaded) and never (re)loaded.
  [wichert]

- Add a language selection portlet.
  [wichert]

- Fixed i18n markup bug in manage-content-type.pt.
  [hannosch]

- Made prevMonth and nextMonth links in calendar portlet to work without
  KSS. This closes http://dev.plone.org/plone/ticket/7052.
  [hannosch]

- Make render_cachekey include the manager and assignment names, otherwise
  portlets that happen to have the same brains in their _data have the same
  cachekey.
  [ldr]


1.0.1
-----

- Remove use of login javascript methods.
  [ree]

- Change event portlet to use getIcon. This fixes
  http://dev.plone.org/plone/ticket/5075.
  [limi]


1.0
---

- Add footer CSS classes to the search portlet. This fixes
  http://dev.plone.org/plone/ticket/6908.
  [wichert]

- Verified translation of month names on the calendar portlet. Found a bit
  of missing i18n markup in the process. This closes
  http://dev.plone.org/plone/ticket/6880.
  [hannosch]

- Wrapped cached render results with a xhtml_compress method taken from
  plone.memoize. This allows you to plug in whitespace removal libraries.
  [hannosch]

- Refactored calendar portlet and moved all calculations to the update
  method instead of doing it in its init.
  [hannosch]

- Use relative links on the calendar portlet for the previous and next
  links, so the portlet can be cached independent of the context.
  [hannosch]

- Cleaned up some templates, added missing i18n markup. This closes
  http://dev.plone.org/plone/ticket/6721.
  [hannosch]

- Fixed erroneous wording in add screen for classicportlet.
  Fixes http://dev.plone.org/plone/ticket/6703
  [elvix]

- Extended the portlet migration machinery to exclude the deprecated
  related and language portlets. This refs
  http://dev.plone.org/plone/ticket/6545.
  [hannosch]

- Cleaned and speeded up calendar portlet. Extinguished some unneeded
  uses of the DateTime module.
  [hannosch]

- Fixed tests to deal with the new default start_level of the navigation
  portlet.
  [hannosch]

- Made the workflow state to show configurable for the news and events
  portlets. This closes http://dev.plone.org/plone/ticket/1395.
  [hannosch]

- Changed the default navigation tree configuration to start at level 1,
  thus there is no longer an overlap with the global navigation section at
  the top. If you want the old behavior back, configure the portlet to
  start at level 0.
  [limi]

- Updated migration code to handle more converted portlets.
  [hannosch]

- Do now show the login portlet if there is no login/password PAS
  extractor configured.
  [wichert]

- Changed 'More news...' to 'More...' on RSS portlet as RSS feeds are not
  always news related. This closes http://dev.plone.org/plone/ticket/6228.
  [sparcd]

- Added <thead> tags to calendar portlet because the <tbody> tags were
  causing it to fail W3C validation.
  [sparcd]

- Duplicate classes in login.pt were causing this to fail W3C HTML checks.
  Have merged the classes as this has a style="display:none" on it anyway.
  This closes http://dev.plone.org/plone/ticket/6241.
  [sparcd]

- Replaced getToolByName with getUtility.
  [hannosch]

- Moved class name from a to li tag for Cornelius (NuPlone skin).
  [jvloothuis]

- Make URLs more ploneish, by removing .html at the end. .html really
  should be reserved for when people create content that way, e.g. if
  uploading from WebDAV. :)
  [optilude]

- Initial implementation.
  [optilude]
