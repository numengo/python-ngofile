# -*- coding: utf-8 -*-
"""
ngofile.exceptions
-----------------------
All exceptions used in the ngofile code base are defined here.
"""
from __future__ import unicode_literals

import gettext
from builtins import str

_ = gettext.gettext


class NgoFileException(Exception):
    """
    Base exception class. All ngofile-specific exceptions should subclass
    this class.
    """


class CopyException(NgoFileException):
    """
    Raised when error occurs during copy
    """


class NotExistingPathException(NgoFileException, IOError):
    """
    Raised when a path does not exist
    """

    def __init__(self, message, path=None):
        if path is not None:
            message = (_('path %(path)s does not exist' % {
                'path': str(path)
            }), message)
        super(NotExistingPathException, self).__init__(message)


class NotADirectoryException(NgoFileException, ValueError):
    """
    Raised when a path is not a directory
    """

    def __init__(self, message, path=None):
        if path is not None:
            message = (_('path %(path)s is not a directory' % {
                'path': str(path)
            }), message)
        super(NotADirectoryException, self).__init__(message)


class NotAZipArchiveException(NgoFileException, ValueError):
    """
    Raised when the object given is not a zipfile
    """
