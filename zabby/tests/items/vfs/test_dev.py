from mock import Mock
from nose.tools import assert_raises, assert_equal, nottest, istest
from zabby.core.exceptions import WrongArgumentError
from zabby.tests import assert_less_equal, assert_is_instance

from zabby.hostos import DiskDeviceStats
from zabby.items.vfs import dev


@nottest
class TestReadWrite():
    def _common_setup(self):
        self.host_os = Mock()
        disk_devices_stats = dict()
        for i in range(2):
            disk_devices_stats['dev{0}'.format(i)] = DiskDeviceStats(
                read_sectors=0, read_operations=3430, read_bytes=0,
                write_sectors=0, write_operations=2277, write_bytes=0
            )
        self.host_os.disk_device_stats.side_effect = (
            lambda x: disk_devices_stats[x])

        def smaller_diskstat(device, shift, now):
            stats = self.host_os.disk_device_stats(device)
            smaller_stats = stats._replace(
                read_operations=stats.read_operations - 100,
                write_operations=stats.write_operations - 100)
            return smaller_stats, 1

        self.host_os.disk_device_stats_shifted.side_effect = smaller_diskstat
        self.host_os.disk_device_names.return_value = set(
            disk_devices_stats.keys())
        self.host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES = set(['operations'])

    def test_raises_exception_if_device_is_unknown(self):
        assert_raises(WrongArgumentError, self.function_under_test,
                      device='wrong', host_os=self.host_os)

    def test_does_not_raise_exception_for_device_all(self):
        self.function_under_test('all')

    def test_raises_exception_if_stat_type_is_unknown(self):
        assert_raises(WrongArgumentError, self.function_under_test,
                      stat_type='wrong', host_os=self.host_os)

    def test_result_for_all_is_greater_than_for_single_device(self):
        results = list()
        devices = self.host_os.disk_device_names()
        for device in devices:
            result = self.function_under_test(device=device,
                                              host_os=self.host_os)
            results.append(result)

        all_result = self.function_under_test(device='all',
                                              host_os=self.host_os)

        for result in results:
            assert_less_equal(result, all_result)

    def test_raises_exception_if_mode_if_unknown(self):
        assert_raises(WrongArgumentError, self.function_under_test,
                      mode='wrong', host_os=self.host_os)

    def test_stats_per_second_returns_float(self):
        result = self.function_under_test(stat_type='ops', host_os=self.host_os)
        assert_is_instance(result, float)

    def test_stats_per_second_returns_zero_if_history_is_empty(self):
        self.host_os.disk_device_stats_shifted.side_effect = None
        self.host_os.disk_device_stats_shifted.return_value = (None, None)
        result = self.function_under_test(stat_type='ops', host_os=self.host_os)
        assert_equal(0, result)


@istest
class TestRead(TestReadWrite):
    def setup(self):
        self.function_under_test = dev.read
        self._common_setup()


@istest
class TestWrite(TestReadWrite):
    def setup(self):
        self.function_under_test = dev.write
        self._common_setup()
