from .. import PloneMessageFactory as _
from ..portlets import base
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from html import unescape
from io import BytesIO
from logging import getLogger
from plone.portlets.interfaces import IPortletDataProvider
from Products.Five.browser.pagetemplatefile import ZopeTwoPageTemplateFile
from urllib.parse import urlsplit
from zope import schema
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import Invalid

import feedparser
import os
import requests
import time

# Accept these bozo_exceptions encountered by feedparser when parsing
# the feed:
ACCEPTED_FEEDPARSER_EXCEPTIONS = (feedparser.CharacterEncodingOverride,)

# store the feeds here (which means in RAM)
FEED_DATA = {}  # url: ({date, title, url, itemlist})

# Try downloading at most this amount of bytes:
MAXIMUM_RSS_FEED_SIZE_BYTES = int(os.getenv("MAXIMUM_RSS_FEED_SIZE_BYTES", 100000))

logger = getLogger(__name__)


def _normal_url_validator(value):
    """Validate that this is a 'normal', external url.

    It should be safe for a visitor to click on.  Of course it could lead to
    a malicious site: we have no way of checking that.
    But at least this must be no javascript url, file url, etc.

    This is used by the '_rss_feed_url_validator' function below,
    which needs to be stricter than this one.

    This function either returns True, or raises Invalid.

    We only return True if the value is good to be used unchanged.
    For example if the value might be fine but there is a space in front:
    we raise Invalid.

    We will probably put a version of this function in plone.base.
    """
    if not value:
        # nothing to validate
        return True
    if value != value.strip():
        raise Invalid(_("URL not accepted"))
    if len(value.splitlines()) > 1:
        raise Invalid(_("URL not accepted"))

    # lowercase for easier checking
    url = value.lower()
    parsed = urlsplit(url)
    scheme = parsed.scheme
    domain = parsed.netloc
    if not scheme:
        # We don't support relative urls, and we don't need to support
        # //example.org
        raise Invalid(_("URL not accepted"))
    if scheme not in ("https", "http"):
        raise Invalid(_("URL not accepted"))

    if not domain:
        # Example: https:example.org
        # When we redirect to this, some browsers fail,
        # others happily go to example.org.
        raise Invalid(_("URL not accepted"))

    # Someone may be doing tricks with escaped html code.
    unescaped_url = unescape(url)
    if unescaped_url != url:
        # Check the unescaped url, then continue checking the current url.
        _normal_url_validator(unescaped_url)

    return True


def _rss_feed_url_validator(value):
    """Validator for RSS feed urls.

    We do not want file:// urls.
    This opens up security issues.
    There are actually more possible problems, so we take over some logic
    from Products.isurlinportal.

    Really this is a validator that we should use for any url that the Plone
    Site itself may make a request to.
    We will probably put a version of this function in plone.base.
    """
    if not value:
        # nothing to validate
        return True
    # lowercase for easier checking
    url = value.lower()

    # The normal url validator already does some basic checks.
    _normal_url_validator(url)

    # We want to go further than that.
    domain = urlsplit(url).netloc

    # We don't want to be used as a port checker.
    if ":" in domain:
        raise Invalid(_("URL not accepted"))

    # We don't want to allow an external visitor to indirectly request
    # content from localhost, or similar, like backend.
    if "." not in domain:
        raise Invalid(_("URL not accepted"))
    if "host.docker.internal" in domain:
        raise Invalid(_("URL not accepted"))

    # Only proper domain names, not IP addresses.
    # We don't want to allow access to private IP addresses.  We could
    # explicitly check the defined ranges, but really it should be fine
    # to only allow proper domain names.
    try:
        [int(part) for part in domain.split(".")]
    except ValueError:
        # At least one part is not an integer.
        pass
    else:
        # All parts are integers.
        raise Invalid(_("URL not accepted"))

    # Someone may be doing tricks with escaped html code.
    unescaped_url = unescape(url)
    if unescaped_url != url:
        # Check the unescaped url, then continue checking the current url.
        _rss_feed_url_validator(unescaped_url)

    return True


def _download_feed_and_headers(url, limit=MAXIMUM_RSS_FEED_SIZE_BYTES):
    """Download an RSS feed from a url.

    The url is trusted: you should have already validated this with the
    _rss_feed_url_validator function.

    We add a timeout and limit the maximum data we read, to avoid requesting
    a 2 GB file.

    This function may raise exceptions from the requests library, or raise its
    own ValueErrors.  The caller should catch and handle this, if wanted.

    For testing, you could create a 10 MB file: `truncate -s 10M 10m.txt`.
    Then run `python -m http.server [optional port]` to serve it.

    For testing if streaming connections are handled correctly, just upload
    a file to Plone (possibly in a separate instance) and use its download
    url.  You can edit `plone.namedfile.utils/__init__.py` function
    `filestream_range_iterator`  and add some logging or a `time.sleep`
    in its `read` method.

    The function returns the contents of the feed, and the response headers.
    """
    if limit <= 0:
        raise ValueError("You must pass a limit for the number of bytes.")
    # Don't allow redirects.  Otherwise that could circumvent our url validator.
    # A connect and read timeout of slightly more than 3 seconds is recommended.
    # See https://docs.python-requests.org/en/latest/user/advanced/#timeouts
    response = requests.get(url, stream=True, allow_redirects=False, timeout=3.5)
    response.raise_for_status()

    # Check the content length header, if it exists.
    length = response.headers.get("Content-Length")
    if length and int(length) > limit:
        raise ValueError("Content-Length header too large")

    # Try to read at most until limit plus 1 bytes.  We may get less, which
    # is fine.  If we get more than the limit, then we refuse: we don't want
    # to load a multi Gigabyte file.  Note that internally this may very
    # well use multiple chunked requests.
    for chunk in response.iter_content(limit + 1):
        if len(chunk) > limit:
            raise ValueError("Downloaded too much content.")
    return chunk, response.headers


class IFeed(Interface):
    def __init__(url, timeout):
        """initialize the feed with the given url. will not automatically load it
        timeout defines the time between updates in minutes
        """

    def loaded():
        """return if this feed is in a loaded state"""

    def title():
        """return the title of the feed"""

    def items():
        """return the items of the feed"""

    def feed_link():
        """return the url of this feed in feed:// format"""

    def site_url():
        """return the URL of the site"""

    def last_update_time_in_minutes():
        """return the time this feed was last updated in minutes since epoch"""

    def last_update_time():
        """return the time the feed was last updated as DateTime object"""

    def needs_update():
        """return if this feed needs to be updated"""

    def update():
        """update this feed. will automatically check failure state etc.
        returns True or False whether it succeeded or not
        """

    def update_failed():
        """return if the last update failed or not"""

    def ok():
        """is this feed ok to display?"""


@implementer(IFeed)
class RSSFeed:
    """an RSS feed"""

    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout

        self._items = []
        self._title = ""
        self._siteurl = ""
        self._loaded = False  # is the feed loaded
        self._failed = False  # does it fail at the last update?
        self._last_update_time_in_minutes = 0  # when was the feed last updated?
        self._last_update_time = None  # time as DateTime or Nonw
        self._etag = None
        self._last_modified = None

    @property
    def last_update_time_in_minutes(self):
        """return the time the last update was done in minutes"""
        return self._last_update_time_in_minutes

    @property
    def last_update_time(self):
        """return the time the last update was done in minutes"""
        return self._last_update_time

    @property
    def update_failed(self):
        return self._failed

    @property
    def ok(self):
        return not self._failed and self._loaded

    @property
    def loaded(self):
        """return whether this feed is loaded or not"""
        return self._loaded

    @property
    def needs_update(self):
        """check if this feed needs updating"""
        now = time.time() / 60
        return (self.last_update_time_in_minutes + self.timeout) < now

    def update(self):
        """update this feed"""
        now = time.time() / 60  # time in minutes

        try:
            # check for failure and retry
            if self.update_failed:
                if (self.last_update_time_in_minutes) < now:
                    return self._retrieveFeed()
                else:
                    return False
            # check for regular update
            if self.needs_update:
                return self._retrieveFeed()
        except Exception:
            self._failed = True
            logger.exception("failed to update RSS feed %s", self.url)

        return self.ok

    def _buildItemDict(self, item):
        link = item.links[0]["href"]
        try:
            link = _normal_url_validator(link)
        except Invalid:
            # We don't want JavaScript links in here.
            logger.warning("Refusing to use link from RSS item %r", link)
            link = ""
        itemdict = {
            "title": item.title,
            "url": link,
            "summary": item.get("description", ""),
        }
        if hasattr(item, "updated"):
            try:
                itemdict["updated"] = DateTime(item.updated)
            except DateTimeError:
                # It's okay to drop it because in the
                # template, this is checked with
                # ``exists:``
                pass

        return itemdict

    def _retrieveFeed(self):
        """do the actual work and try to retrieve the feed"""
        url = self.url
        if url:
            # Prevent loading local file: urls and other possible hacks.
            try:
                _rss_feed_url_validator(url)
            except Invalid:
                logger.warning("Refusing to load stored RSS url %r", url)
                url = ""
        if url != "":
            self._last_update_time_in_minutes = time.time() / 60
            self._last_update_time = DateTime()
            kwargs = {}
            if self._last_modified:
                kwargs["modified"] = self._last_modified
            if self._etag:
                kwargs["etag"] = self._etag
            # Initially we simply passed the url, but that can be a method
            # of attack, especially if this points to a very large file.
            # So we first download it ourselves, then pass the contents.
            # TODO pass those kwargs to our requests function.
            # TODO Then check for 304, to replace what we do a few lines down.
            contents, headers = _download_feed_and_headers(url)
            download = BytesIO(contents)
            # `feedparser.parse`` says: When a URL is not passed, the feed
            # location to use in relative URL resolution should be passed
            # in the `Content-Location` response header.
            # kwargs["response_headers"] = {"Content-Location": url}
            # But the `Content-Type` header is also required.
            # Let's pass all of them.
            # lowercase all of the HTTP headers for comparisons per RFC 2616
            # That is what feedparser does when it loads a url.
            response_headers = {k.lower(): v for k, v in headers.items()}
            d = feedparser.parse(download, response_headers=response_headers)
            if getattr(d, "bozo", 0) == 1 and not isinstance(
                d.get("bozo_exception"), ACCEPTED_FEEDPARSER_EXCEPTIONS
            ):
                self._loaded = True  # we tried at least but have a failed load
                self._failed = True
                logger.info(
                    "failed to update RSS feed %s", d.get("bozo_exception", None)
                )
                return False

            #  If the response was 304, nothing changed!
            #  Don't change anything...
            if d.status != 304:
                self._etag = getattr(d, "etag", None)
                self._modified = getattr(d, "modified", None)

                try:
                    self._title = d.feed.title
                except AttributeError:
                    self._title = ""
                try:
                    self._siteurl = d.feed.link
                except AttributeError:
                    self._siteurl = ""

                self._items = []
                for item in d["items"]:
                    try:
                        itemdict = self._buildItemDict(item)
                    except AttributeError:
                        continue

                    self._items.append(itemdict)

            self._loaded = True
            self._failed = False
            return True
        self._loaded = True
        self._failed = True  # no url set means failed
        return False  # no url set, although that should not really happen

    @property
    def items(self):
        return self._items

    # convenience methods for displaying
    #

    @property
    def feed_link(self):
        """return rss url of feed for portlet"""
        return self.url.replace("http://", "feed://")

    @property
    def title(self):
        """return title of feed for portlet"""
        return self._title

    @property
    def siteurl(self):
        """return the link to the site the RSS feed points to"""
        return self._siteurl


class IRSSPortlet(IPortletDataProvider):
    portlet_title = schema.TextLine(
        title=_("Title"),
        description=_(
            "Title of the portlet.  If omitted, the title of the " "feed will be used."
        ),
        required=False,
        default="",
    )

    count = schema.Int(
        title=_("Number of items to display"),
        description=_("How many items to list."),
        required=True,
        default=5,
    )

    url = schema.TextLine(
        title=_("URL of RSS feed"),
        description=_("Link of the RSS feed to display."),
        required=True,
        constraint=_rss_feed_url_validator,
        default="",
    )

    timeout = schema.Int(
        title=_("Feed reload timeout"),
        description=_("Time in minutes after which the feed should be " "reloaded."),
        required=True,
        default=100,
    )


@implementer(IRSSPortlet)
class Assignment(base.Assignment):
    portlet_title = ""

    @property
    def title(self):
        """return the title with RSS feed title or from URL"""
        feed = FEED_DATA.get(self.data.url, None)
        if feed is None:
            return "RSS: " + self.url[:20]
        else:
            return "RSS: " + feed.title[:20]

    def __init__(self, portlet_title="", count=5, url="", timeout=100):
        self.portlet_title = portlet_title
        self.count = count
        self.url = url
        self.timeout = timeout


class Renderer(base.DeferredRenderer):
    render_full = ZopeTwoPageTemplateFile("rss.pt")

    @property
    def initializing(self):
        """should return True if deferred template should be displayed"""
        feed = self._getFeed()
        if not feed.loaded:
            return True
        if feed.needs_update:
            return True
        return False

    def deferred_update(self):
        """refresh data for serving via KSS"""
        feed = self._getFeed()
        feed.update()

    def update(self):
        """update data before rendering. We can not wait for KSS since users
        may not be using KSS."""
        self.deferred_update()

    def _getFeed(self):
        """return a feed object but do not update it"""
        feed = FEED_DATA.get(self.data.url, None)
        if feed is None:
            # create it
            feed = FEED_DATA[self.data.url] = RSSFeed(self.data.url, self.data.timeout)
        return feed

    @property
    def url(self):
        """return url of feed for portlet"""
        return self._getFeed().url

    @property
    def siteurl(self):
        """return url of site for portlet"""
        return self._getFeed().siteurl

    @property
    def feedlink(self):
        """return rss url of feed for portlet"""
        return self.data.url.replace("http://", "feed://")

    @property
    def title(self):
        """return title of feed for portlet"""
        return getattr(self.data, "portlet_title", "") or self._getFeed().title

    @property
    def feedAvailable(self):
        """checks if the feed data is available"""
        return self._getFeed().ok

    @property
    def items(self):
        return self._getFeed().items[: self.data.count]

    @property
    def enabled(self):
        return self._getFeed().ok


class AddForm(base.AddForm):
    schema = IRSSPortlet
    label = _("Add RSS Portlet")
    description = _("This portlet displays an RSS feed.")

    def create(self, data):
        return Assignment(
            portlet_title=data.get("portlet_title", ""),
            count=data.get("count", 5),
            url=data.get("url", ""),
            timeout=data.get("timeout", 100),
        )


class EditForm(base.EditForm):
    schema = IRSSPortlet
    label = _("Edit RSS Portlet")
    description = _("This portlet displays an RSS feed.")
