from mock import Mock
from nose.tools import assert_raises

from zabby.tests import assert_not_in
from zabby.core.exceptions import WrongArgumentError
from zabby.core.utils import SIZE_CONVERSION_MODES
from zabby.items.vfs import fs

FS = '/'
TOTAL_FS_SIZE = 23506452480
FREE_FS_SIZE = 6913863680


class TestFsSize():
    def setup(self):
        self.host_os = Mock()
        self.host_os.fs_size.return_value = (FREE_FS_SIZE, TOTAL_FS_SIZE)

    def test_throws_exception_on_wrong_arguments(self):
        assert_raises(WrongArgumentError, fs.size, FS, 'wrong')

    def test_gathers_information_from_host_os(self):
        fs.size(FS, host_os=self.host_os)
        self.host_os.fs_size.assert_called_with(FS)

    def test_different_modes_produce_different_results(self):
        results = list()
        for conversion_mode in SIZE_CONVERSION_MODES:
            result = fs.size(FS, conversion_mode, self.host_os)
            assert_not_in(result, results)
            results.append(result)
