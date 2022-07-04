from plone.portlets.manager import PortletManager

import doctest


# Standard options for DocTests
optionflags = (
    doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_ONLY_FIRST_FAILURE
)


# Helper class for tests
class FooPortletManager(PortletManager):
    pass
