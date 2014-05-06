#!/usr/bin/env python

import os
import sys

__file__ = os.path.normpath(os.path.abspath(__file__))
__path__ = os.path.dirname(__file__)

libs_path = os.path.join(__path__, 'libs')
if libs_path not in sys.path:
    sys.path.insert(0, libs_path)

arch_path = os.path.join(__path__, 'arch')
if arch_path not in sys.path:
    sys.path.insert(0, arch_path)

prymatex_path = os.path.abspath(os.path.join(__path__, '../../prymatex'))
if prymatex_path not in sys.path:
    sys.path.insert(0, prymatex_path)
    # Install 
    from prymatex import resources
    resources.installCustomFromThemeMethod()

from codeintel.base import autocomplete

class Selection(object):
    def end(self):
        return 1
    def start(self):
        return 0
        
class Editor(object):
    def id(self):
        return 2
    
    def sel(self):
        print("Selection")
        return [ Selection() ]

if __name__ == '__main__':
    path = None
    pos = 0
    lang = "Python"
    autocomplete(Editor(), 0, 0, ('calltips', 'cplns'), True, args=[path, pos, lang])
