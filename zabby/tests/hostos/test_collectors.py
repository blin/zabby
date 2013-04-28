from mock import Mock, patch
from nose.tools import assert_equal
from zabby.tests import assert_less_equal, assert_is_instance

from zabby.hostos import HostOS, DiskDeviceStats, CpuTimes, CPU_TIMES
from zabby.hostos.collectors import DiskDeviceStatsCollector, CpuTimesCollector


class TestHostOSCollectors():
    def setup(self):
        self.host_os = HostOS()
        self.collectors = list()
        for i in range(2):
            collector = Mock()
            self.collectors.append(collector)
            self.host_os._collectors.append(collector)

    def test_start_collectors_runs_every_collector(self):
        self.host_os.start_collectors()
        for collector in self.collectors:
            collector.run.assert_called_once_with()

    def test_stop_collectors_stops_every_collector(self):
        self.host_os.stop_collectors()
        for collector in self.collectors:
            collector.stop.assert_called_once_with()


DEVICE_NAME = 'dev0'


class TestDiskDeviceStatsCollector():
    def setup(self):
        self._patcher = patch('zabby.hostos.collectors.time')
        self.mock_time = self._patcher.start()

        self.now = 0

        def increment_and_return_now():
            self.now += 1
            return self.now

        self.mock_time.side_effect = increment_and_return_now

        self.host_os = Mock()

        self.stat = 0

        def increment_and_return_stats(device):
            self.stat += 1
            return DiskDeviceStats(
                read_sectors=0, read_operations=self.stat, read_bytes=0,
                write_sectors=0, write_operations=0, write_bytes=0
            )

        self.host_os.disk_device_stats.side_effect = increment_and_return_stats
        self.host_os.disk_device_names.return_value = set([DEVICE_NAME])

        self.shift = 5
        self.current_time = self.shift + 1
        self.collector = DiskDeviceStatsCollector(self.shift, self.host_os)

    def teardown(self):
        self._patcher.stop()

    def test_returns_none_if_history_is_empty(self):
        stats, timestamp = self.collector.get_stats(DEVICE_NAME, self.shift,
                                                    self.current_time)
        assert_equal((None, None), (stats, timestamp))

    def test_returns_not_completely_shifted_stats_for_unfilled_history(self):
        self.collector._collect()

        stats, timestamp = self.collector.get_stats(DEVICE_NAME, self.shift,
                                                    self.current_time)
        assert_less_equal(self.shift, self.current_time - timestamp)
        assert_is_instance(stats, DiskDeviceStats)

    def test_returns_completely_shifted_stats_for_filled_history(self):
        for i in range(self.shift + 1):
            self.collector._collect()

        stats, timestamp = self.collector.get_stats(DEVICE_NAME, self.shift,
                                                    self.current_time)
        assert_equal(self.shift, self.current_time - timestamp)
        assert_is_instance(stats, DiskDeviceStats)


class TestCpuTimesCollector:
    def setup(self):
        self.host_os = Mock()
        self.host_os.cpu_count.return_value = 2
        self.host_os.cpu_times.return_value = CpuTimes(*[0 for _ in CPU_TIMES])

        self.shift = 5
        self.collector = CpuTimesCollector(self.shift, self.host_os)

    def test_returns_none_if_history_is_empty(self):
        cpu_count = self.host_os.cpu_count()
        for cpu_id in range(cpu_count):
            times = self.collector.get_times(cpu_id, self.shift)
            assert_equal(None, times)

    def test_returns_cpu_times_for_unfilled_history(self):
        self.collector._collect()

        cpu_count = self.host_os.cpu_count()
        for cpu_id in range(cpu_count):
            times = self.collector.get_times(cpu_id, self.shift)
            assert_is_instance(times, CpuTimes)

    def test_returns_cpu_times_for_filled_history(self):
        for i in range(self.shift + 1):
            self.collector._collect()

        cpu_count = self.host_os.cpu_count()
        for cpu_id in range(cpu_count):
            times = self.collector.get_times(cpu_id, self.shift)
            assert_is_instance(times, CpuTimes)
