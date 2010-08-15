# -*- coding: utf-8 -*-
"""
    test_versioning
    ~~~~~~~~~~~~~~~

    Test the versioning implementation.

    :copyright: Copyright 2007-2010 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
import pickle

from util import *

from docutils.statemachine import ViewList
from docutils.parsers.rst.directives.html import MetaBody

from sphinx import addnodes
from sphinx.versioning import make_diff, add_uids, merge_doctrees

def setup_module():
    global app, original, original_uids
    app = TestApp()
    app.builder.env.app = app
    app.connect('doctree-resolved', on_doctree_resolved)
    app.build()
    original = doctrees['versioning/original']
    original_uids = [n.uid for n in add_uids(original, is_paragraph)]

def teardown_module():
    app.cleanup()
    (test_root / '_build').rmtree(True)

doctrees = {}

def on_doctree_resolved(app, doctree, docname):
    doctrees[docname] = doctree

def test_make_diff():
    tests = [
        (('aaa', 'aaa'), (True, False, False)),
        (('aaa', 'aab'), (False, True, False)),
        (('aaa', 'abb'), (False, True, False)),
        (('aaa', 'aba'), (False, True, False)),
        (('aaa', 'baa'), (False, True, False)),
        (('aaa', 'bbb'), (False, False, True))
    ]
    for args, result in tests:
        assert make_diff(*args) == result

def is_paragraph(node):
    return node.__class__.__name__ == 'paragraph'

def test_add_uids():
    assert len(original_uids) == 3

def test_picklablility():
    # we have to modify the doctree so we can pickle it
    copy = original.copy()
    copy.reporter = None
    copy.transformer = None
    copy.settings.warning_stream = None
    copy.settings.env = None
    copy.settings.record_dependencies = None
    for metanode in copy.traverse(MetaBody.meta):
        metanode.__class__ = addnodes.meta
    loaded = pickle.loads(pickle.dumps(copy, pickle.HIGHEST_PROTOCOL))
    assert all(getattr(n, 'uid', False) for n in loaded.traverse(is_paragraph))

def test_modified():
    modified = doctrees['versioning/modified']
    new_nodes = list(merge_doctrees(original, modified, is_paragraph))
    uids = [n.uid for n in modified.traverse(is_paragraph)]
    assert not new_nodes
    assert original_uids == uids

def test_added():
    added = doctrees['versioning/added']
    new_nodes = list(merge_doctrees(original, added, is_paragraph))
    uids = [n.uid for n in added.traverse(is_paragraph)]
    assert len(new_nodes) == 1
    assert original_uids == uids[:-1]

def test_deleted():
    deleted = doctrees['versioning/deleted']
    new_nodes = list(merge_doctrees(original, deleted, is_paragraph))
    uids = [n.uid for n in deleted.traverse(is_paragraph)]
    assert not new_nodes
    assert original_uids[::2] == uids

def test_deleted_end():
    deleted_end = doctrees['versioning/deleted_end']
    new_nodes = list(merge_doctrees(original, deleted_end, is_paragraph))
    uids = [n.uid for n in deleted_end.traverse(is_paragraph)]
    assert not new_nodes
    assert original_uids[:-1] == uids

def test_insert():
    insert = doctrees['versioning/insert']
    new_nodes = list(merge_doctrees(original, insert, is_paragraph))
    uids = [n.uid for n in insert.traverse(is_paragraph)]
    assert len(new_nodes) == 1
    assert original_uids[0] == uids[0]
    assert original_uids[1:] == uids[2:]