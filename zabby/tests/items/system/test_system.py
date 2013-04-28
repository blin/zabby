from mock import Mock
from nose.tools import assert_raises
from zabby.core.exceptions import WrongArgumentError

from zabby.items import system


class TestSystem():
    def setup(self):
        self.host_os = Mock()
        self.host_os.AVAILABLE_HOSTNAME_TYPES = set(['host'])

    def test_hostname_raises_exception_if_hostname_type_is_unknown(self):
        assert_raises(WrongArgumentError, system.hostname, 'wrong',
                      host_os=self.host_os)
