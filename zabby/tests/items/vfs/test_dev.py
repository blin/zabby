from mock import Mock
from nose.tools import assert_raises
from zabby.core.exceptions import WrongArgumentError
from zabby.tests import assert_less_equal

from zabby.hostos import DiskDeviceStats
from zabby.items.vfs import dev


class TestRead():
    def setup(self):
        self.host_os = Mock()
        disk_devices_stats = dict()
        for i in range(2):
            disk_devices_stats['dev{0}'.format(i)] = DiskDeviceStats(
                read_sectors=0, read_operations=3430, read_bytes=0,
                write_sectors=0, write_operations=2277, write_bytes=0
            )
        self.host_os.disk_device_stats.side_effect = (
            lambda x: disk_devices_stats[x])
        self.host_os.disk_device_names.return_value = set(
            disk_devices_stats.keys())
        self.host_os.AVAILABLE_DISK_DEVICE_STATS_TYPES = set(['operations'])

    def test_raises_exception_if_device_is_unknown(self):
        assert_raises(WrongArgumentError, dev.read, device='wrong',
                      host_os=self.host_os)

    def test_does_not_raise_exception_for_device_all(self):
        dev.read('all')

    def test_raises_exception_if_stat_type_is_unknown(self):
        assert_raises(WrongArgumentError, dev.read, stat_type='wrong',
                      host_os=self.host_os)

    def test_result_for_all_is_greater_than_for_single_device(self):
        results = list()
        devices = self.host_os.disk_device_names()
        for device in devices:
            result = dev.read(device=device, host_os=self.host_os)
            results.append(result)

        all_result = dev.read(device='all', host_os=self.host_os)

        for result in results:
            assert_less_equal(result, all_result)
