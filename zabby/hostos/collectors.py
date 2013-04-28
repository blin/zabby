from collections import defaultdict, deque
import logging
from time import time, sleep

LOG = logging.getLogger(__name__)


class Collector:
    """
    Collector continuously runs in the background and collects information
    (usually from host_os) for later aggregation
    """

    def __init__(self, interval, host_os):
        self._host_os = host_os
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

    def __init__(self, max_shift, interval, host_os):
        Collector.__init__(self, interval, host_os)
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
