from mock import Mock
from nose.tools import assert_raises, nottest, istest

from zabby.tests import assert_not_in, assert_less_equal
from zabby.core.exceptions import WrongArgumentError
from zabby.core.utils import SIZE_CONVERSION_MODES
from zabby.items.vfs import fs

FS = '/'
FREE_FS_SIZE, TOTAL_FS_SIZE = 6913863680, 23506452480
FREE_FS_INODES, TOTAL_FS_INODES = 1102585, 1457776


@nottest
class TestFsFunction():
    def test_throws_exception_on_wrong_arguments(self):
        assert_raises(WrongArgumentError, fs.size, FS, 'wrong')

    def test_gathers_information_from_host_os(self):
        self.function_under_test(FS, host_os=self.host_os)
        self.host_os_function.assert_called_with(FS)

    def test_different_modes_produce_different_results(self):
        results = list()
        for conversion_mode in SIZE_CONVERSION_MODES:
            result = self.function_under_test(FS, conversion_mode, self.host_os)
            assert_not_in(result, results)
            results.append(result)

    def test_all_modes_produce_positive_results(self):
        for conversion_mode in SIZE_CONVERSION_MODES:
            result = self.function_under_test(FS, conversion_mode, self.host_os)
            assert_less_equal(0, result)


@istest
class TestFsSize(TestFsFunction):
    def setup(self):
        self.host_os = Mock()
        self.host_os_function = Mock()
        self.host_os_function.return_value = (FREE_FS_SIZE, TOTAL_FS_SIZE)
        self.host_os.fs_size = self.host_os_function
        self.function_under_test = fs.size


@istest
class TestFsInodes(TestFsFunction):
    def setup(self):
        self.host_os = Mock()
        self.host_os_function = Mock()
        self.host_os_function.return_value = (FREE_FS_INODES, TOTAL_FS_INODES)
        self.host_os.fs_inodes = self.host_os_function
        self.function_under_test = fs.inode