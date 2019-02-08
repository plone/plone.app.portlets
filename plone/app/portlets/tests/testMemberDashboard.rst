Setup::

    >>> user1, pass1 = 'user1', 'pass1'
    >>> user2, pass2 = 'user2', 'pass2'
    >>> portal = layer['portal']
    >>> uf = portal.acl_users
    >>> uf.userFolderAddUser(user1, pass1, ['Member'], [])
    >>> uf.userFolderAddUser(user2, pass2, ['Member'], [])
    >>> import transaction
    >>> transaction.commit()
    >>> import re
    >>> from plone.protect.authenticator import createToken


bug: 11174: Portal Members can't add portlets to their dashboard
----------------------
Login as the 'user1' user

    >>> from plone.testing.z2 import Browser
    >>> browser = Browser(layer['app'])
    >>> portalURL = portal.absolute_url()

    >>> browser.open(portalURL + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'user1'
    >>> browser.getControl(name='__ac_password').value = 'pass1'
    >>> browser.getControl('Log in').click()

Go to the dashboard and check that portlets are addable here

    >>> browser.open(portal.absolute_url()+'/@@dashboard')
    >>> browser.getLink('Edit').click()
    >>> 'Add portlet' in browser.contents
    True

Let's try to add a Search portlet and then remove it

    >>> bool(re.search('\<\/span\>\s+Search\s+\<\/div\>', browser.contents))
    False
    >>> browser.getControl(name=':action',index=0).value = ['/++dashboard++plone.dashboard1+user1/+/portlets.Search']
    >>> browser.getForm(index=1).submit()
    >>> browser.getControl('Save').click()  # This submits the now shown add form.
    >>> browser.open(portalURL+'/@@manage-dashboard')
    >>> '/search/edit' in browser.contents
    True
    >>> browser.getControl(name="search-remove").click()
    >>> '/search/edit' in browser.contents
    False

Now, let's try to add a portlet using the addview

    >>> browser.open(portalURL+'/@@manage-dashboard')
    >>> browser.open(portalURL + "/++dashboard++plone.dashboard1+user1/+/portlets.Search?referer="+portalURL)
    >>> browser.getControl('Save').click()  # This submits the now shown add form.
    >>> browser.open(portalURL+'/@@manage-dashboard')
    >>> '/search/edit' in browser.contents
    True
    >>> browser.getControl(name="search-remove").click()
    >>> '/search/edit' in browser.contents
    False

Using the addview, let's see that we cannot add a portlet for another user

    >>> browser.open(portalURL+'/@@manage-dashboard')
    >>> browser.open(portalURL + "/++dashboard++plone.dashboard1+user2/+/portlets.Search?referer="+portalURL)
    >>> "Insufficient Privileges" in browser.contents
    True

    >>> browser.open(portalURL + '/logout')

    >>> browser.open(portalURL + '/login_form')
    >>> browser.getControl(name='__ac_name').value = 'user2'
    >>> browser.getControl(name='__ac_password').value = 'pass2'
    >>> browser.getControl('Log in').click()

    >>> browser.open(portalURL+'/@@manage-dashboard?_authenticator=' + createToken())
    >>> bool(re.search('\<\/span\>\s+Search\s+\<\/div\>', browser.contents))
    False

Now, we try to open the @@manage-portlets view and also try to call the addview
for a portlet. We shouldn't be able to do any of this

    >>> browser.open(portalURL+'/@@manage-portlets?_authenticator=' + createToken())
    >>> "Insufficient Privileges" in browser.contents
    True
    >>> browser.open(portalURL + "/++contextportlets++plone.leftcolumn/+/portlets.Search?_authenticator=" + createToken())
    >>> "Insufficient Privileges" in browser.contents
    True

Finally, if we add the "Member" role to the "Portlets: Manage portlets" permission, we should be able to call
those views

    >>> portal.manage_permission('Portlets: Manage portlets', roles=['Manager', 'Member'], acquire=0)
    >>> transaction.commit()
    >>> browser.open(portalURL+'/@@manage-portlets?_authenticator=' + createToken())
    >>> "Insufficient Privileges" in browser.contents
    False
    >>> bool(re.search('\<\/span\>\s+Search\s+\<\/div\>', browser.contents))
    False
    >>> browser.open(portalURL + "/++contextportlets++plone.leftcolumn/+/portlets.Search")
    >>> "Insufficient Privileges" in browser.contents
    False
    >>> browser.getControl('Save').click()  # This submits the now shown add form.
    >>> '/search/edit' in browser.contents
    True
