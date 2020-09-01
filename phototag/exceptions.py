"""
exceptions.py

Stores all exceptions used by the application in a single file for organization purposes.
"""


class PhototagException(Exception):
    """Base class for exceptions in this project/module."""


class UserError(PhototagException):
    """Exception most likely caused by the user."""


class InvalidSelectionError(UserError):
    """File selection was invalid."""
    pass


class InvalidConfigurationError(UserError):
    """The configuration presented to the application was not valid or workable."""
    pass


class EmptyConfigurationValueError(InvalidConfigurationError):
    """The configuration did not include values required to run the application."""
    pass


class NoSidecarFileError(PhototagException):
    """
    The application is confused as a sidecar file was not found where it was expected.

    Most RAW files processed by Adobe are accompanied by a .xmp file with the same name.
    """
    pass
