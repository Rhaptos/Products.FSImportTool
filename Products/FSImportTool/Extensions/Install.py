from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
import string

def install(self):
    """Add the tool"""
    out = StringIO()

    # Add the tool
    urltool = getToolByName(self, 'portal_url')
    portal = urltool.getPortalObject();
    try:
        portal.manage_delObjects('portal_fsimport')
        out.write("Removed old portal_fsimport tool\n")
    except:
        pass  # we don't care if it fails
    portal.manage_addProduct['FSImportTool'].manage_addTool('FSImport Tool', None)
    out.write("Adding FSImport Tool\n")

    return out.getvalue()
