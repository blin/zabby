import collections
import time

from nose.plugins.attrib import attr
from nose.tools import assert_raises

from zabby.core.exceptions import OperatingSystemError
from zabby.core.six import integer_types, string_types
from zabby.hostos import (detect_host_os, NetworkInterfaceInfo, ProcessInfo,
                          DiskDeviceStats, CpuTimes, SystemLoad)
from zabby.tests import assert_is_instance, assert_less, assert_in


PRESENT_FILESYSTEM = '/'
PRESENT_INTERFACE = 'lo'


@attr(os='linux')
class TestLinux():
    def setup(self):
        from zabby.hostos.linux import Linux

        self.linux = Linux()

    def test_linux_is_detected_correctly(self):
        detected_os = detect_host_os()
        assert_is_instance(detected_os, self.linux.__class__)

    def test_fs_size_returns_tuple_of_integers_one_less_than_other(self):
        free, total = self.linux.fs_size(PRESENT_FILESYSTEM)

        assert_is_instance(free, integer_types)
        assert_is_instance(total, integer_types)

        assert_less(free, total)

    def test_fs_inodes_returns_tuple_of_integers_one_less_than_other(self):
        free, total = self.linux.fs_inodes(PRESENT_FILESYSTEM)

        assert_is_instance(free, integer_types)
        assert_is_instance(total, integer_types)

        assert_less(free, total)

    def test_net_interface_names_returns_set_of_strings(self):
        interface_names = self.linux.net_interface_names()

        assert_is_instance(interface_names, set)
        for interface_name in interface_names:
            assert_is_instance(interface_name, string_types)
        assert_in(PRESENT_INTERFACE, interface_names)

    def test_net_interface_info_returns_NetworkInterfaceInfo(self):
        interface_names = self.linux.net_interface_names()
        interface_info = self.linux.net_interface_info(interface_names.pop())

        assert_is_instance(interface_info, NetworkInterfaceInfo)
        for key, value in interface_info._asdict().items():
            assert_is_instance(value, integer_types)

    def test_process_infos_returns_iterable_of_ProcessInfo(self):
        process_infos = list(self.linux.process_infos())

        for process_info in process_infos:
            assert_is_instance(process_info, ProcessInfo)

    def test_process_infos_contains_processes_run_by_root(self):
        process_infos = [proc_info
                         for proc_info in self.linux.process_infos()
                         if proc_info.uid == 0]

        # at least init should be here
        assert_less(0, len(process_infos))

    def test_uid_returns_integer(self):
        uid = self.linux.uid('root')

        assert_is_instance(uid, integer_types)

    def test_uid_raises_exception_on_invalid_username(self):
        assert_raises(OperatingSystemError, self.linux.uid, '')

    def test_memory_returns_dict_of_numbers(self):
        d = self.linux.memory()

        assert_is_instance(d, dict)
        for key, value in d.items():
            assert_is_instance(value, (integer_types, float))

    def test_memory_dict_contains_all_available_memory_types(self):
        d = self.linux.memory()

        for memory_type in self.linux.AVAILABLE_MEMORY_TYPES:
            assert_in(memory_type, d)

    def test_disk_device_names_returns_set_of_strings(self):
        device_names = self.linux.disk_device_names()

        assert_is_instance(device_names, set)

        for device_name in device_names:
            assert_is_instance(device_name, string_types)

    def test_disk_device_stats_returns_DiskDeviceStats(self):
        device_names = self.linux.disk_device_names()

        disk_device_stats = self.linux.disk_device_stats(device_names.pop())

        assert_is_instance(disk_device_stats, DiskDeviceStats)

        for key, value in disk_device_stats._asdict().items():
            assert_is_instance(value, integer_types)

    def test_cpu_count_returns_integer(self):
        cpu_count = self.linux.cpu_count()
        assert_is_instance(cpu_count, integer_types)

    def test_cpu_times(self):
        cpu_id = list(range(self.linux.cpu_count())).pop()

        cpu_times = self.linux.cpu_times(cpu_id)

        assert_is_instance(cpu_times, CpuTimes)

    def test_hostname(self):
        hostname = self.linux.hostname('host')
        assert_is_instance(hostname, string_types)

    def test_uname(self):
        uname = self.linux.uname()
        assert_is_instance(uname, collections.Iterable)

    def test_uptime(self):
        uptime = self.linux.uptime()
        assert_is_instance(uptime, integer_types)

    def test_max_number_of_running_processes(self):
        maxproc = self.linux.max_number_of_running_processes()
        assert_is_instance(maxproc, integer_types)

    def test_system_load(self):
        system_load = self.linux.system_load()
        assert_is_instance(system_load, SystemLoad)


@attr(os='linux')
class TestLinuxCollectors():
    def setup(self):
        from zabby.hostos.linux import Linux

        self.linux = Linux()

    def test_disk_device_collector_collection(self):
        self.linux._disk_device_stats_collector._collect()

        devices = self.linux.disk_device_names()
        now = int(time.time())
        (stats, timestamp) = self.linux.disk_device_stats_shifted(devices.pop(),
                                                                  60, now)
        assert_is_instance(stats, DiskDeviceStats)

    def test_cpu_times_collector_collection(self):
        self.linux._cpu_times_collector._collect()

        cpu_id = list(range(self.linux.cpu_count())).pop()

        times = self.linux._cpu_times_collector.get_times(cpu_id, 60)

        assert_is_instance(times, CpuTimes)
