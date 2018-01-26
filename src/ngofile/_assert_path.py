# coding: utf-8
""" misc copy utilities
"""
from __future__ import unicode_literals

import gettext
import logging
import sys
from builtins import range
from builtins import str
from pathlib import Path

from .exceptions import NgoFileException
from .exceptions import NotADirectoryException
from .exceptions import NotExistingPathException

_ = gettext.gettext


def assert_Path(path, exists=False, is_dir=False, arrays=True):
    """ asserts a path, test if it exists or if it is a directory or throw exception

    :param path: path to assert
    :type path: string or pathlib.Path or list of string or pathlib.Path
    :param exists: test if path exists
    :param is_dir: test if path is a directory
    :param arrays: handle arrays
    :rtype: pathlib.Path or list of pathlib.Path """
    logger = logging.getLogger(__name__)
    if not path:
        raise NgoFileException(_('input path is None'))
    if isinstance(path, list):
        if not array:
            raise NgoFileException('input is a list')
        return [assert_Path(p, exists, is_dir) for p in path]
    if not isinstance(path, Path):
        try:
            path = Path(path.__str__())
        except TypeError:
            e = NgoFileException(
                _('unable to create path from %(path)s' % {
                    'path': str(path)
                }))
            logger.exception(e)
            raise e
    if exists and not path.exists():
        e = NotExistingPathException('', path)
        logger.exception(e)
        raise e
    if is_dir and not path.is_dir():
        e = NotADirectoryException('', path)
        logger.exception(e)
        raise e
    return path
