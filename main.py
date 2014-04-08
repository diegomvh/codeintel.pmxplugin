#!/usr/bin/env python
from __future__ import print_function

VERSION = "1.0"

import os
import sys
import datetime
import stat
import time
import threading
import logging
from cStringIO import StringIO

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

libs_path = os.path.join(__path__, 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

arch_path = os.path.join(__path__, 'arch')
if arch_path not in sys.path:
    sys.path.insert(0, arch_path)

arch_path = os.path.abspath(os.path.join(__path__, '../../../Projects/prymatex'))
if arch_path not in sys.path:
    sys.path.insert(0, arch_path)

from prymatex import get_git_changeset

from codeintel2.common import (CodeIntelError, EvalTimeout, LogEvalController,
    TRG_FORM_DEFN, TRG_FORM_CPLN, TRG_FORM_CALLTIP)
from codeintel2.manager import Manager

despaired = False

codeintel_log = logging.getLogger("codeintel")
condeintel_log_filename = ''
condeintel_log_file = None
_ci_mgr_ = {}

def pos2bytes(content, pos):
    return len(content[:pos].encode('utf-8'))

def codeintel_manager(folders_id):
    folders_id = None
    global _ci_mgr_, condeintel_log_filename, condeintel_log_file
    mgr = _ci_mgr_.get(folders_id)
    if mgr is None:
        for thread in threading.enumerate():
            if thread.name == "CodeIntel Manager":
                thread.finalize() # this finalizes the index, citadel and the manager and waits them to end (join)
        mgr = Manager(
            extra_module_dirs=None,
            db_base_dir=None, # os.path.expanduser(os.path.join('~', '.codeintel', 'databases', folders_id)),
            db_catalog_dirs=[],
            db_import_everything_langs=None,
        )
        mgr.upgrade()
        mgr.initialize()

        # Connect the logging file to the handler
        condeintel_log_filename = os.path.join(mgr.db.base_dir, 'codeintel.log')
        condeintel_log_file = open(condeintel_log_filename, 'w', 1)
        codeintel_log.handlers = [logging.StreamHandler(condeintel_log_file)]
        msg = "Starting logging SublimeCodeIntel v%s rev %s (%s) on %s" % (VERSION, get_revision()[:12], os.stat(__file__)[stat.ST_MTIME], datetime.datetime.now().ctime())
        print("%s\n%s" % (msg, "=" * len(msg)), file=condeintel_log_file)

        _ci_mgr_[folders_id] = mgr
    return mgr

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


if __name__ == '__main__':
    mgr = codeintel_manager(12)
    print(mgr.get_citadel_langs())
    print(list(mgr.db.get_catalogs_zone().avail_catalogs()))
    path = None
    lang = "Python"
    env = {}
    content = "import os\n\ndef pepe():\n    pass\np = os. "
    pos = 39
    forms = ('defns', 'cplns', 'calltips')
    start = time.time()
    print(pos2bytes(content, pos), content[pos])
    def _codeintel(buf):
        cplns = None
        calltips = None
        defns = None
    
        if not buf:
            return [None] * len(forms)
    
        try:
            trg = getattr(buf, 'preceding_trg_from_pos', lambda p: None)(pos2bytes(content, pos), pos2bytes(content, pos))
            defn_trg = getattr(buf, 'defn_trg_from_pos', lambda p: None)(pos2bytes(content, pos))
        except (CodeIntelError):
            codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
            trg = None
            defn_trg = None
        except:
            codeintel_log.exception("Exception! %s:%s (%s)" % (path or '<Unsaved>', pos, lang))
            raise
        else:
            eval_log_stream = StringIO()
            _hdlrs = codeintel_log.handlers
            hdlr = logging.StreamHandler(eval_log_stream)
            hdlr.setFormatter(logging.Formatter("%(name)s: %(levelname)s: %(message)s"))
            codeintel_log.handlers = list(_hdlrs) + [hdlr]
            ctlr = LogEvalController(codeintel_log)
            try:
                if 'cplns' in forms and trg and trg.form == TRG_FORM_CPLN:
                    cplns = buf.cplns_from_trg(trg, ctlr=ctlr, timeout=20)
                if 'calltips' in forms and trg and trg.form == TRG_FORM_CALLTIP:
                    calltips = buf.calltips_from_trg(trg, ctlr=ctlr, timeout=20)
                if 'defns' in forms and defn_trg and defn_trg.form == TRG_FORM_DEFN:
                    defns = buf.defns_from_trg(defn_trg, ctlr=ctlr, timeout=20)
            except EvalTimeout:
                pass
            finally:
                codeintel_log.handlers = _hdlrs
            result = False
            merge = ''
            for msg in reversed(eval_log_stream.getvalue().strip().split('\n')):
                msg = msg.strip()
                if msg:
                    try:
                        name, levelname, msg = msg.split(':', 2)
                        name = name.strip()
                        levelname = levelname.strip().lower()
                        msg = msg.strip()
                    except:
                        merge = (msg + ' ' + merge) if merge else msg
                        continue
                    merge = ''
                    if not result and msg.startswith('evaluating '):
                        result = True
        ret = []
        for f in forms:
            if f == 'cplns':
                ret.append(cplns)
            elif f == 'calltips':
                ret.append(calltips)
            elif f == 'defns':
                ret.append(defns)
        print(ret)
        total = (time.time() - start) * 1000
        if total > 1000:
            timestr = "~%ss" % int(round(total / 1000))
        else:
            timestr = "%sms" % int(round(total))
        if not despaired or total < timeout:
            msg = "Done '%s' CodeIntel! Full CodeIntel took %s" % (lang, timestr)
            print(msg, file=condeintel_log_file)

            def _callback():
                view_sel = view.sel()
                if view_sel and view.line(view_sel[0]) == view.line(pos):
                    callback(*ret)
        else:
            msg = "Just finished indexing '%s'! Please try again. Full CodeIntel took %s" % (lang, timestr)
            print(msg, file=condeintel_log_file)

    buf = mgr.buf_from_content(content, lang, env, path or "<Unsaved>", 'utf-8')
    buf.scan()
    _codeintel(buf)
