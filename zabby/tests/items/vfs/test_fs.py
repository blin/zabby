from mock import Mock
from nose.tools import assert_raises, istest

from zabby.items.vfs import fs
from zabby.tests import TestSizeFunction

FS = '/'
FREE_FS_SIZE, TOTAL_FS_SIZE = 6913863680, 23506452480
FREE_FS_INODES, TOTAL_FS_INODES = 1102585, 1457776


@istest
class TestFsSize(TestSizeFunction):
    def setup(self):
        self.host_os = Mock()
        self.host_os_function = Mock()
        self.host_os_function.return_value = (FREE_FS_SIZE, TOTAL_FS_SIZE)
        self.host_os.fs_size = self.host_os_function
        self.function_under_test = fs.size
        self.target = FS


@istest
class TestFsInodes(TestSizeFunction):
    def setup(self):
        self.host_os = Mock()
        self.host_os_function = Mock()
        self.host_os_function.return_value = (FREE_FS_INODES, TOTAL_FS_INODES)
        self.host_os.fs_inodes = self.host_os_function
        self.function_under_test = fs.inode
        self.target = FS
