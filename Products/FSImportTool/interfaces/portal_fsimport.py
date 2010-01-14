# Copyright (c) 2003 The Connexions Project, All Rights Reserved
# Written by Brent Hendricks

""" File system import interface"""

from Interface import Attribute
try:
    from Interface import Interface
except ImportError:
    # for Zope versions before 2.6.0
    from Interface import Base as Interface

class portal_fsimport(Interface):
    """Defines an interface for a tool that provides import/export
    facilities between the ZODB and the filesystem"""

    id = Attribute('id','Must be set to "portal_fsimport"')

    def importFromFS(path, container):
        """
        Recursively import 'path' from the filesystem into the specified container.
        'container' must be a PortalFolder-like object
        """

    def exportToFS(path, object):
        """
        Recursively export 'object' to the filesystem.
        'path' must be an absolute-path to a directory on the filesystem
        """
    
