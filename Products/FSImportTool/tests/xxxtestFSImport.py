#
# FSImportTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import tempfile
import BaseTestCase
from Products.FSImportTool.FSImportTool import FSImportError

class TestFSImportTool(BaseTestCase.BaseTestCase):
    """Test the portal_fsimport tool's import function"""

    def testInterface(self):
        from Products.FSImportTool.interfaces.portal_fsimport import portal_fsimport
        self.assertEqual(portal_fsimport.isImplementedBy(self.fs_import), 1)

    def testImportNonAbsolute(self):
        """importFromFS should error on relative paths"""
        self.assertRaises(FSImportError, self.fs_import.importFromFS, 'relative', None)

    def testImportNonExistentPath(self):
        """importFromFS should error on non-existent paths"""
        self.assertRaises(FSImportError, self.fs_import.importFromFS, '/non-existent/path', None)

    def testImportUnreadablePath(self):
        """importFromFS should error on unreadable paths"""
        import tempfile
        fd, path = tempfile.mkstemp()
        os.chmod(path, 0)
        self.assertRaises(FSImportError, self.fs_import.importFromFS, path, None)
        os.unlink(path)

    def testImportIntoNonContainer(self):
        """importFromFS requires a container"""
        import tempfile
        fd, path = tempfile.mkstemp()
        self.assertRaises(FSImportError, self.fs_import.importFromFS, path, None)
        os.unlink(path)

    def testImportTextFile(self):
        """import single text file"""
        fd, path = tempfile.mkstemp()
        name = os.path.basename(path)
        msg = 'Test content'
        f = os.fdopen(fd, 'w')
        f.write(msg)
        f.close()
        self.fs_import.importFromFS(path, self.folder)
        obj = getattr(self.folder.aq_base, name)
        self.assertEqual(obj.portal_type, 'File')
        self.assertEqual(obj.data, msg)
        os.unlink(path)

    def testImportImageFile(self):
        """import single image file"""
        fd, path = tempfile.mkstemp('.png')
        name = os.path.basename(path)
        self.fs_import.importFromFS(path, self.folder)
        obj = getattr(self.folder.aq_base, name)
        self.assertEqual(obj.portal_type, 'Image')
        os.unlink(path)

    def testImportEmptyFolder(self):
        """import an empty folder"""
        path = tempfile.mkdtemp()
        name = os.path.basename(path)
        self.fs_import.importFromFS(path, self.folder)
        obj = getattr(self.folder.aq_base, name)
        self.assertEqual(obj.portal_type, 'Folder')
        os.rmdir(path)

    def testResursiveImport(self):
        """recursive import on tree"""
        path = tempfile.mkdtemp()
        name = os.path.basename(path)

        f1_path = os.path.join(path, 'f1')
        f1 = file(f1_path, 'w')
        f1.write('some content')
        f1.close

        d1_path = os.path.join(path, 'd1') 
        os.mkdir(d1_path)

        f2_path = os.path.join(d1_path, 'f2')
        f2 = file(f2_path, 'w')
        f2.write('some more content')
        f2.close

        self.fs_import.importFromFS(path, self.folder)
        obj = getattr(self.folder.aq_base, name)
        f1 = obj.f1
        d1 = obj.aq_explicit.d1
        f2 = d1.aq_explicit.f2

        os.unlink(f1_path)
        os.unlink(f2_path)
        os.rmdir(d1_path)
        os.rmdir(path)

        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestFSImportTool))
        return suite

