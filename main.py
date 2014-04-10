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

from codeintel2.common import (CodeIntelError, EvalTimeout, LogEvalController,
    TRG_FORM_DEFN, TRG_FORM_CPLN, TRG_FORM_CALLTIP)
from codeintel.manager import codeintel_manager, codeintel_scan
from codeintel.utils import pos2bytes



codeintel_log = logging.getLogger("codeintel")
condeintel_log_filename = ''
condeintel_log_file = None
_ci_mgr_ = {}

if __name__ == '__main__':
    mgr = codeintel_manager(str(hash(frozenset([]))))
    print("Available: %s" % ', '.join(set(mgr.get_citadel_langs() + mgr.get_cpln_langs())))
                    
    path = None
    lang = "JavaScript"
    env = {}
    contentJavaScript = "window. "
    contentPython = "import os\n\ndef pepe():\n    pass\np = os. "
    content = contentJavaScript
    pos = 5
    forms = ('defns', 'cplns', 'calltips')
    start = time.time()
    print(pos2bytes(content, pos), content[pos])
    def _codeintel(buf, msgs):
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
        print(ret, msgs)
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
    
    codeintel_scan(path, content, lang, callback=_codeintel, pos=pos, forms=forms)
