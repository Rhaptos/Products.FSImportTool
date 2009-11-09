"""
Tool to import and export files between the filesystem and the ZODB

Author: Brent Hendricks
(C) 2005 Rice University

This software is subject to the provisions of the GNU Lesser General
Public License Version 2.1 (LGPL).  See LICENSE.txt for details.
"""

import os
import mimetypes
import zLOG
import AccessControl
from Products.CMFCore.utils import UniqueObject
from Products.CMFCore.utils import getToolByName
from OFS.SimpleItem import SimpleItem
from Globals import InitializeClass
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from Products.CMFCore.CMFCorePermissions import View, ManagePortal
from interfaces.portal_fsimport import portal_fsimport as IFSImportTool

class FSImportError(Exception):
    pass

class FSExportError(Exception):
    pass

class FSImportTool(UniqueObject, SimpleItem):

    __implements__ = (IFSImportTool)

    id = 'portal_fsimport'
    meta_type = 'FSImport Tool'
    security = AccessControl.ClassSecurityInfo()

    manage_options=(( {'label':'Overview', 'action':'manage_overview'},
                      ) + SimpleItem.manage_options
                    )

    ##   ZMI methods
    security.declareProtected(ManagePortal, 'manage_overview')
    manage_overview = PageTemplateFile('zpt/explainFSImportTool', globals() )

    # IFSImportTool Interface fulfillment 

    def importFromFS(self, path, container):
        """Import filesystem path into container"""
        if not os.path.isabs(path):
            raise FSImportError, path + ' not an absolute path'

        if not os.path.exists(path):
            raise FSImportError, path + ' does not exist'

        if not os.access(path, os.R_OK):
            raise FSImportError, path + ' not readable'
        
        # FIXME: perhaps we should test for a specific interface?
        if not hasattr(container, 'isPrincipiaFolderish'):
            raise FSImportError, path + ' not readable'

        name = os.path.basename(path)
        if os.path.isdir(path):
            getToolByName(self, 'portal_types').constructContent('Folder', container, name)
            folder = getattr(container.aq_explicit, name)
            for name in os.listdir(path):
                fullpath = os.path.join(path, name)
                self.importFromFS(fullpath, folder)
        else:
            self._importFile(path, container)

    def exportToFS(self, path, object):
        """Export object to filesystem"""
        if not os.path.isabs(path):
            raise FSExportError, path + ' not an absolute path'

        if not os.path.exists(path):
            raise FSExportError, path + ' does not exist'

        if not os.path.isdir(path):
            raise FSExportError, path + ' not a directory'

        if not os.access(path, os.W_OK):
            raise FSExportError, path + ' not writable'

        if object.isPrincipiaFolderish:
            folder_path = os.path.join(path, object.getId())
            if os.path.exists(folder_path):
                if not os.path.isdir(folder_path):
                    raise FSExportError, folder_path + ' exists and is not a directory'
            else:
                os.mkdir(folder_path)
            for child in object.objectValues():
                self.exportToFS(folder_path, child)
        else:
            self._exportFile(object, path)

    def _exportFile(self, obj, path):
        """Export a ZODB file to the file system"""
        # Work only on this object
        obj = obj.aq_base

        data = _getFileContents(obj)
        # Don't export objects with no content
        # FIXME: If we ever do properties we'll have to do this better
        if data is None:
            return

        # Ensure that fspath/path exists.
        if not os.path.exists(path):
            os.makedirs(path)

        # Create/replace file
        file = open(os.path.join(path, obj.getId()), 'wb')
        if (type(data) == type('') or type(data) == type(u'')):
            if type(data) is unicode:
                data = data.encode('utf-8')
            file.write(data)
        else:
            while data is not None:
                file.write(data.data)
                data = data.next
        file.close()


    def _importFile(self, path, container):
        """Import a file from the filesystem into the specified ZODB container"""

        name = os.path.basename(path)
        typ, encoding = mimetypes.guess_type(path)
        f = file(path, 'r')
        body = f.read()
        f.close()

        registry = getToolByName(self, 'content_type_registry')
        if not registry:
            portal_type = 'File'
        portal_type = registry.findTypeName(name, typ, body) or 'File'

        getToolByName(self, 'portal_types').constructContent(portal_type, container, name, file=body)


InitializeClass(FSImportTool)


# Convenience functions

def _getFileContents(obj):
    """Try various method of getting at the file's contents"""
    fnctns = ('get_data',)
    for f in fnctns:
        data = getattr(obj, f, None)
        if data is not None:
            return data()
    attrs = ('text', 'raw', 'data')
    for a in attrs:
        data = getattr(obj, a, None)
        if data is not None:
            return data
    else:
        return None
    

