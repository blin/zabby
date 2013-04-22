from mock import Mock
from nose.tools import assert_raises, assert_equal
from zabby.core.exceptions import WrongArgumentError, OperatingSystemError

from zabby.hostos import ProcessInfo
from zabby.items import proc
from zabby.tests import assert_greater


PROCESS_NAME = 'systemd'
PROCESS_UID = 1000
PROCESS_USER = 'user'
PROCESS_STATE = 'sleep'
PROCESS_COMMAND_LINE = '/sbin/init'


class TestNum():
    def setup(self):
        self.host_os = Mock()

        self.processes = [
            ProcessInfo(PROCESS_NAME, 0, PROCESS_STATE,
                        PROCESS_COMMAND_LINE, 0),
            ProcessInfo('bash', PROCESS_UID, 'run', '/bin/bash', 0),
        ]
        self.host_os.process_infos.return_value = self.processes

        self.host_os.uid.side_effect = lambda x: {PROCESS_USER: PROCESS_UID}[x]

    def test_raises_exception_if_state_is_invalid(self):
        assert_raises(WrongArgumentError, proc.num, state='wrong')

    def test_raises_exception_if_user_is_invalid(self):
        self.host_os.uid.side_effect = OperatingSystemError
        assert_raises(OperatingSystemError, proc.num, user='wrong')

    def test_default_matches_all(self):
        value = proc.num(host_os=self.host_os)

        assert_equal(len(self.processes), value)

    def test_name_filter_works(self):
        value = proc.num(name=PROCESS_NAME, host_os=self.host_os)

        assert_greater(len(self.processes), value)

    def test_user_filter_works(self):
        value = proc.num(user=PROCESS_USER, host_os=self.host_os)

        assert_greater(len(self.processes), value)

    def test_user_filter_works(self):
        value = proc.num(state=PROCESS_STATE, host_os=self.host_os)

        assert_greater(len(self.processes), value)

    def test_user_filter_works(self):
        value = proc.num(cmdline=PROCESS_COMMAND_LINE, host_os=self.host_os)

        assert_greater(len(self.processes), value)

    def test_multiple_filter_conditions_match(self):
        value = proc.num(name=PROCESS_NAME, state=PROCESS_STATE,
                         host_os=self.host_os)

        assert_greater(len(self.processes), value)

    def test_not_all_filter_conditions_match(self):
        value = proc.num(name='wrong', state=PROCESS_STATE,
                         host_os=self.host_os)

        assert_equal(0, value)
