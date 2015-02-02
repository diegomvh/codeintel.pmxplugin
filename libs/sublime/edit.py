#!/usr/bin/env python

class Edit(object):
    """Edit objects have no functions, they exist to group buffer modifications.
    Edit objects are passed to TextCommands, and are not user createable. Using an invalid Edit object, or an Edit object from a different view, will cause the functions that require them to fail. 
    """
    pass