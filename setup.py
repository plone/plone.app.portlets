from setuptools import setup, find_packages

version = '3.0.5'

setup(name='plone.app.portlets',
      version=version,
      description="Plone integration for the basic plone.portlets package",
      long_description=open("README.rst").read() + "\n" +
                       open("CHANGES.rst").read(),
      classifiers=[
          "Environment :: Web Environment",
          "Framework :: Plone",
          "Framework :: Zope2",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
        ],
      keywords='portlets viewlets plone',
      author='Plone Foundation',
      author_email='plone-developers@lists.sourceforge.net',
      url='http://pypi.python.org/pypi/plone.app.portlets',
      license='GPL version 2',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages = ['plone', 'plone.app'],
      include_package_data=True,
      zip_safe=False,
      extras_require=dict(
          test=[
              'Products.ATContentTypes',
              'plone.app.blob',
              'plone.app.testing',
          ],
      ),
      install_requires=[
        'setuptools',
        'five.customerize',
        'plone.i18n',
        'plone.memoize',
        'plone.portlets>=1.1',
        'plone.app.i18n',
        'plone.app.layout >= 1.2dev',
        'plone.app.vocabularies >= 2.1.15.dev0',
        'transaction',
        'zope.annotation',
        'zope.browser',
        'zope.component',
        'zope.configuration',
        'zope.container',
        'zope.contentprovider',
        'zope.event',
        'zope.i18nmessageid',
        'zope.interface',
        'zope.lifecycleevent',
        'zope.publisher',
        'zope.schema',
        'zope.site',
        'zope.traversing',
        'Products.CMFPlone',
        'Products.CMFCore',
        'Products.CMFDynamicViewFTI',
        'Products.GenericSetup',
        'Products.PluggableAuthService',
        'ZODB3',
        'Acquisition',
        'DateTime',
        'Zope2 >= 2.12.3',
        'feedparser',
      ],
      )
