#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

def registerPlugin(manager, descriptor):
    libs_path = os.path.join(descriptor.path, 'libs')
    if libs_path not in sys.path:
        sys.path.insert(0, libs_path)
    
    arch_path = os.path.join(descriptor.path, 'arch')
    if arch_path not in sys.path:
        sys.path.insert(0, arch_path)
    
    from codeintel2.manager import Manager
