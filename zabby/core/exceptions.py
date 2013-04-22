class ConfigurationError(Exception):
    """ Something is wrong with configuration """


class WrongArgumentError(Exception):
    """ Wrong argument was passed to a function"""


class OperatingSystemError(Exception):
    """ Operating system behaved in an unusual manner """