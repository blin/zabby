from collections import defaultdict, deque
import logging
from time import time, sleep

LOG = logging.getLogger(__name__)


class Collector(object):
    """
    Collector continuously runs in the background and collects information
    (usually from host_os) for later aggregation
    """

    def __init__(self, interval):
        self._running = False
        self._interval = interval

    def _collect(self):
        raise NotImplementedError

    def run(self):
        self._running = True
        while self._running:
            self._collect()
            sleep(self._interval)

    def stop(self):
        self._running = False


class DiskDeviceStatsCollector(Collector):
    """
    Collects disk device stats

    :depends on: [host_os.disk_device_names, host_os.disk_device_stats]
    """

    def __init__(self, max_shift, host_os):
        super(DiskDeviceStatsCollector, self).__init__(1)
        self._host_os = host_os
        self._history = defaultdict(lambda: deque(maxlen=max_shift + 1))

    def _collect(self):
        devices = self._host_os.disk_device_names()

        for device in devices:
            stats = self._host_os.disk_device_stats(device)
            timestamp = int(time())
            self._history[device].appendleft((stats, timestamp))

    def get_stats(self, device, shift, now):
        """
        Returns DiskDeviceStats for device shifted for shift seconds from now
        and timestamp for when this stats were taken
        """
        stats, timestamp = self._find_shifted_stats(self._history[device], now,
                                                    shift)

        return stats, timestamp

    def _find_shifted_stats(self, device_history, now, shift):
        best_candidate = (None, None)
        for diskstat, timestamp in device_history:
            best_candidate = (diskstat, timestamp)
            if (now - timestamp) >= shift:
                break
        return best_candidate


class CpuTimesCollector(Collector):
    """
    Collects cpu times

    :depends on: [host_os.cpu_count, host_os.cpu_times]
    """
    def __init__(self, max_shift, host_os):
        super(CpuTimesCollector, self).__init__(1)
        self._host_os = host_os
        self._history = defaultdict(lambda: deque(maxlen=max_shift + 1))

    def _collect(self):
        cpu_count = self._host_os.cpu_count()
        for cpu_id in range(cpu_count):
            cpu_times = self._host_os.cpu_times(cpu_id)
            self._history[cpu_id].appendleft(cpu_times)

    def get_times(self, cpu_id, shift):
        cpu_history = self._history[cpu_id]
        if len(cpu_history) == 0:
            return None

        best_candidate = min(shift, len(cpu_history) - 1)

        return cpu_history[best_candidate]
