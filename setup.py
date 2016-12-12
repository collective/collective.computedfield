from setuptools import setup, find_packages

version = '0.1dev0'

setup(
    name='collective.computedfield',
    version=version,
    description="zope.schema field for computed values",
    long_description=(open("README.rst").read()),
    classifiers=[
        "Programming Language :: Python",
        "Framework :: ZODB",
        "Framework :: Zope3",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        ],
    keywords='',
    author='Sean Upton',
    author_email='sean.upton@hsc.utah.edu',
    url='https://github.com/collective/collective.computedfield',
    license='MIT',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'plone.supermodel',
        'plone.schemaeditor',
        'setuptools',
        'zope.component',
        'zope.schema',
        'zope.i18nmessageid',
        'Products.GenericSetup',
        'z3c.form',
        # -*- Extra requirements: -*-
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
