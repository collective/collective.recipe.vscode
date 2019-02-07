# -*- coding: utf-8 -*-
"""Doctest runner for 'plone.recipe.sublimetext'."""
from zc.buildout.testing import read  # noqa: F401
from zope.testing import renormalizing

import doctest
import os
import re
import unittest
import zc.buildout.testing
import zc.buildout.tests


__docformat__ = 'restructuredtext'

optionflags = (
    doctest.ELLIPSIS |
    doctest.NORMALIZE_WHITESPACE |
    doctest.REPORT_ONLY_FIRST_FAILURE
)

test_dir = os.path.abspath(os.path.dirname(__file__))


def setUp(test):

    zc.buildout.testing.buildoutSetUp(test)

    # Install the recipe (and dependencies) in develop mode
    zc.buildout.testing.install_develop('zc.recipe.egg', test)
    zc.buildout.testing.install_develop('plone.recipe.sublimetext', test)


def tearDown(test):

    zc.buildout.testing.buildoutTearDown(test)


def test_suite():
    suite = unittest.TestSuite((
            doctest.DocFileSuite(
                'recipe.rst',
                globs=globals(),
                setUp=setUp,
                tearDown=tearDown,
                optionflags=optionflags,
                checker=renormalizing.RENormalizing([
                        # If want to clean up the doctest output you
                        # can register additional regexp normalizers
                        # here. The format is a two-tuple with the RE
                        # as the first item and the replacement as the
                        # second item, e.g.
                        # (re.compile('my-[rR]eg[eE]ps'), 'my-regexps')
                        zc.buildout.testing.normalize_path,
                        zc.buildout.testing.not_found,

                        # don't count subversion dirs in ls() output
                        (re.compile(r'^\s*?d\s+.svn\s*?^', re.MULTILINE | re.DOTALL), ''),
                        ]),
                ),
            ))
    return suite
