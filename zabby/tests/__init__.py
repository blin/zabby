from nose.tools import assert_true

# assert_is_instance appeared in python 3.2 and was backported to 2.7
try:
    from nose.tools import assert_is_instance
except ImportError:
    def assert_is_instance(obj, cls, msg=None):
        assert_true(isinstance(obj, cls), msg)

# assert_not_in and assert_less appeared in python 3.1 and was backported to 2.7
try:
    from nose.tools import assert_not_in
    from nose.tools import assert_less
    from nose.tools import assert_less_equal
except ImportError:
    def assert_not_in(member, collection, msg=None):
        assert_true(member not in collection, msg)

    def assert_less(a, b, msg=None):
        assert_true(a < b, msg)

    def assert_less_equal(a, b, msg=None):
        assert_true(a <= b, msg)
