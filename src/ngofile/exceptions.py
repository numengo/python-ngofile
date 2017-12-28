# -*- coding: utf-8 -*-
"""
ngofile.exceptions
-----------------------
All exceptions used in the ngofile code base are defined here.
"""
from __future__ import unicode_literals


class NgoFileException(Exception):
    """
    Base exception class. All ngofile-specific exceptions should subclass
    this class.
    """


class NotExistingPathException(NgoFileException, IOError):
    """
    Raised when a path does not exist
    """


class NotADirectoryException(NgoFileException, ValueError):
    """
    Raised when a path is not a directory
    """
