# coding: utf-8
""" misc copy utilities
"""
from __future__ import unicode_literals
from builtins import range
from builtins import str

import logging
import sys
from pathlib import Path
import gettext

from .exceptions import NgoFileException, NotExistingPathException, NotADirectoryException

_ = gettext.gettext

def assert_Path(path,exists=False,is_dir=False, vector=True):
    """ asserts a path, test if it exists or if it is a directory or throw exception

    :param path: path to assert
    :type path: string or pathlib.Path or list of string or pathlib.Path
    :param exists: test if path exists
    :param is_dir: test if path is a directory
    :param vector: handle vectors
    :rtype: pathlib.Path or list of pathlib.Path """
    logger = logging.getLogger(__name__)
    if not path:
        raise Exception(_('input path is None'))
    if isinstance(path,list):
        if not vector:
            raise Exception('input is a vector')
        return [assert_Path(p,exists,is_dir) for p in path]
    if not isinstance(path,Path):
        try:
            path = Path(str(path))
        except TypeError:
            e = NgoFileException(_('unable to create path from %(path)s' % {'path':str(path)}))
            logger.exception(e)
            raise e
    if exists and not path.exists():
        e = NotExistingPathException('',path)
        logger.exception(e)
        raise e
    if is_dir and not path.is_dir():
        e = NotADirectoryException('',path)
        logger.exception(e)
        raise e
    return path
