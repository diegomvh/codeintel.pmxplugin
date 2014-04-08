#!/usr/bin/env python

import os
import stat

from prymatex import get_git_changeset

def pos2bytes(content, pos):
    return len(content[:pos].encode('utf-8'))

__path__ = os.path.dirname(__file__)

def get_revision(path=None):
    """
:returns: Revision number of this branch/checkout, if available. None if
no revision number can be determined.
"""
    path = os.path.abspath(os.path.normpath(__path__ if path is None else path))
    while path and path != '/' and path != '\\':
        rev = get_git_changeset(path)
        if rev:
            return u'GIT-%s' % rev
        uppath = os.path.abspath(os.path.join(path, '..'))
        if uppath != path:
            path = uppath
        else:
            break
    return u'GIT-unknown'

def tryGetMTime(filename):
    if filename:
        return os.stat(filename)[stat.ST_MTIME]
    return 0
    
def find_back(start_at, look_for):
    root = os.path.realpath('/')
    start_at = os.path.abspath(start_at)
    if not os.path.isdir(start_at):
        start_at = os.path.dirname(start_at)
    if start_at == root:
        return None
    while True:
        if look_for in os.listdir(start_at):
            return os.path.join(start_at, look_for)
        continue_at = os.path.abspath(os.path.join(start_at, '..'))
        if continue_at == start_at or continue_at == root:
            return None
        start_at = continue_at


def updateCodeIntelDict(master, partial):
    for key, value in partial.items():
        if isinstance(value, dict):
            master.setdefault(key, {}).update(value)
        elif isinstance(value, (list, tuple)):
            master.setdefault(key, []).extend(value)


def tryReadDict(filename, dictToUpdate):
    if filename:
        file = open(filename, 'r')
        try:
            updateCodeIntelDict(dictToUpdate, eval(file.read()))
        finally:
            file.close()