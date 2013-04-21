from nose.tools import assert_raises, assert_equal
from zabby.tests import assert_is_instance

from zabby.core import utils
from zabby.core.exceptions import WrongArgumentError
from zabby.core.six import integer_types
from zabby.core.utils import SIZE_CONVERSION_MODES, validate_mode, convert_size


def test_validate_mode_raises_exception_if_mode_is_not_available():
    assert_raises(WrongArgumentError, utils.validate_mode, 'mode', [])


def test_validate_mode_does_not_raise_exception_if_mode_is_available():
    validate_mode('mode', ['mode'])


def test_convert_size_returns_integers_or_floats():
    free, total = 50, 100
    for conversion_mode in SIZE_CONVERSION_MODES:
        converted_size = convert_size(free, total, conversion_mode)
        assert_is_instance(converted_size, (float, integer_types))


def test_convert_size_returns_zero_if_total_size_is_zero():
    assert_equal(0, convert_size(1, 0, SIZE_CONVERSION_MODES[0]))
