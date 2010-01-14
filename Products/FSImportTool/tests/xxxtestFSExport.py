#
# FSImportTool tests
#

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

import tempfile
import BaseTestCase
from Products.FSImportTool.FSImportTool import FSExportError

class TestFSExport(BaseTestCase.BaseTestCase):
    """Test the portal_fsimport tool's export function"""

    def testExportNonAbsolute(self):
        """exportToFS should error on relative paths"""
        self.assertRaises(FSExportError, self.fs_import.exportToFS, 'relative', None)

    def testExportNonExistentPath(self):
        """exportToFS should error on non-existent paths"""
        self.assertRaises(FSExportError, self.fs_import.exportToFS, '/non-existent/path', None)

    def testExportNonDirectoryPath(self):
        """exportToFS should error on non-directory paths"""
        import tempfile
        fd, path = tempfile.mkstemp()
        self.assertRaises(FSExportError, self.fs_import.exportToFS, path, None)
        os.unlink(path)

    def testExportUnwritablePath(self):
        """exportToFS should error on unwritable paths"""
        import tempfile
        path = tempfile.mkdtemp()
        os.chmod(path, 0)
        self.assertRaises(FSExportError, self.fs_import.exportToFS, path, None)
        os.rmdir(path)

    def testExportTextFile(self):
        """export single text file"""
        self.folder.invokeFactory('File', 'f1', file='Test content')
        path = tempfile.mkdtemp()
        self.fs_import.exportToFS(path, self.folder.f1)

        f1_path = os.path.join(path, 'f1')
        f1 = file(f1_path)
        self.assertEquals(f1.read(), 'Test content')
        f1.close()
        
        os.unlink(f1_path)
        os.rmdir(path)

    def testExportEmptyFolder(self):
        """export an empty folder"""
        self.folder.invokeFactory('Folder', 'd1')
        path = tempfile.mkdtemp()
        self.fs_import.exportToFS(path, self.folder.d1)

        d1_path = os.path.join(path, 'd1')
        self.assertEquals(os.path.isdir(d1_path), 1)
        
        os.rmdir(d1_path)
        os.rmdir(path)

    def testResursiveExport(self):
        """recursive export on tree"""
        self.folder.invokeFactory('Folder', 'd1')
        self.folder.d1.invokeFactory('File', 'f1', file='Test content')
        self.folder.d1.invokeFactory('Folder', 'd2')
        self.folder.d1.d2.invokeFactory('File', 'f2', file='Test more content')

        path = tempfile.mkdtemp()
        self.fs_import.exportToFS(path, self.folder.d1)

        d1_path = os.path.join(path, 'd1')
        f1_path = os.path.join(d1_path, 'f1')
        d2_path = os.path.join(d1_path, 'd2')
        f2_path = os.path.join(d2_path, 'f2')

        self.assertEquals(os.path.isdir(d1_path), 1)
        f1 = file(f1_path)
        self.assertEquals(f1.read(), 'Test content')
        self.assertEquals(os.path.isdir(d2_path), 1)
        f2 = file(f2_path)
        self.assertEquals(f2.read(), 'Test more content')
        f1.close()
        f2.close()

        os.unlink(f2_path)
        os.rmdir(d2_path)
        os.unlink(f1_path)
        os.rmdir(d1_path)
        os.rmdir(path)

        
if __name__ == '__main__':
    framework()
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestFSExport))
        return suite

