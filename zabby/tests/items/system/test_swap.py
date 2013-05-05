from mock import Mock
from nose.tools import istest, assert_raises, nottest
from zabby.core.exceptions import WrongArgumentError
from zabby.core.six import integer_types
from zabby.items.system.swap import SWAP_TO_DISK_DEVICE_STAT
from zabby.tests import TestSizeFunction, assert_is_instance

from zabby.hostos import SwapInfo, DiskDeviceStats
from zabby.items.system import swap

FREE_SWAP_SIZE, TOTAL_SWAP_SIZE = 10733772800, 10737414144
SWAP_DEVICE = 'sda4'


@istest
class TestSwapSize(TestSizeFunction):
    def setup(self):
        self.host_os = Mock()
        self.host_os_function = Mock()
        self.host_os_function.return_value = (FREE_SWAP_SIZE, TOTAL_SWAP_SIZE)
        self.host_os.swap_size = self.host_os_function
        self.function_under_test = swap.size
        self.target = SWAP_DEVICE


@nottest
class TestIntoOutOf():
    def _common_setup(self):
        self.host_os = Mock()
        self.host_os.swap_info.return_value = SwapInfo(read=10153, write=25087)
        self.host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES = set(['sectors',
                                                              'operations'])
        self.host_os.swap_device_names.return_value = set([SWAP_DEVICE])
        self.host_os.disk_device_stats.return_value = DiskDeviceStats(
            read_sectors=1, read_operations=2, read_bytes=0,
            write_sectors=2, write_operations=3, write_bytes=0
        )

    def test_raises_exception_when_trying_to_use_pages_without_all(self):
        assert_raises(WrongArgumentError, self.function_under_test,
                      device=SWAP_DEVICE, mode='pages', host_os=self.host_os)

    def test_pages_returns_integer(self):
        result = self.function_under_test(mode='pages', host_os=self.host_os)

        assert_is_instance(result, integer_types)

    def test_raises_exception_for_unknown_mode(self):
        assert_raises(WrongArgumentError, self.function_under_test,
                      mode='wrong',
                      host_os=self.host_os)

    def test_raises_exception_for_known_unavailable_mode(self):
        unavailable_mode = 'sectors'
        self.host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES.remove(unavailable_mode)
        assert_raises(WrongArgumentError, self.function_under_test,
                      mode=unavailable_mode, host_os=self.host_os)

    def test_raises_exception_for_unknown_device(self):
        self.host_os.swap_device_names.return_value = set()
        assert_raises(WrongArgumentError, self.function_under_test,
                      device=SWAP_DEVICE,
                      host_os=self.host_os)

    def test_does_not_raise_exception_for_device_all(self):
        self.function_under_test(device=SWAP_DEVICE, host_os=self.host_os)

    def test_disk_device_stat_types_returns_integer(self):
        for mode in SWAP_TO_DISK_DEVICE_STAT.keys():
            result = self.function_under_test(mode=mode, host_os=self.host_os)
            assert_is_instance(result, integer_types)


@istest
class TestSwapIntoMemory(TestIntoOutOf):
    def setup(self):
        self._common_setup()
        self.function_under_test = swap.into_memory


@istest
class TestSwapOutOfMemory(TestIntoOutOf):
    def setup(self):
        self._common_setup()
        self.function_under_test = swap.out_of_memory
