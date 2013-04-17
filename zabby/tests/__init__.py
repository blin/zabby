# assert_is_instance appeared in python 3.2 and was backported to 2.7
try:
    from nose.tools import assert_is_instance
except ImportError:
    from nose.tools import assert_true

    def assert_is_instance(obj, cls, msg=None):
        assert_true(isinstance(obj, cls), msg)