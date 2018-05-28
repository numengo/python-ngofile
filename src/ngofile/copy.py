# coding: utf-8
""" 
Misc copy utilities
"""
from __future__ import unicode_literals

import filecmp
import fnmatch
import gettext
import logging
import os
import os.path
import re
import shutil
import sys
from builtins import range
from builtins import str
from pathlib import Path

from future.utils import text_to_native_str

from .exceptions import CopyException
from .exceptions import NgoFileException
from .exceptions import NotADirectoryException
from .exceptions import NotExistingPathException

enc = sys.stdout.encoding or "cp850"
_ = gettext.gettext


def _copy(src, dst):
    """
    Copy a file src to dst (directory).
    
    If dst exists and is the same, nothing is done

    :param src: source file or directory
    :type src:pathlib.Path
    :param dst: destination file or directory
    :type dst:pathlib.Path
    """
    logger = logging.getLogger(__name__)
    src = text_to_native_str(src)
    dst = text_to_native_str(dst)
    if os.path.exists(dst) and os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.exists(dst):
        if not filecmp.cmp(src, dst):
            logger.debug('updating ' + str(dst, enc))
            shutil.copy2(src, dst)
        else:
            pass
            # logger.info(unicode(dst,enc) + ' already up to date')
    else:
        logger.debug('copy ' + str(src, enc) + ' to ' + str(dst, enc))
        shutil.copy2(src, dst)


def _copytree(src, dst, excludes=[], includes=[], recursive=True):
    """ 
    Copy a directory structure src to destination
    
    :param src: source file or directory
    :type src: path
    :param dst: destination file or directory
    :type dst: path
    :param excludes: list of patterns to exclude
    :type excludes: ngomodel.validators.List
    :param includes: list of patterns to include
    :type includes: ngomodel.validators.List
    :param recursive: recursive copy
    """
    logger = logging.getLogger(__name__)
    # make sure to convert string from ngopath
    # convert everything to ngopath and back to string
    src = text_to_native_str(src)
    dst = text_to_native_str(dst)

    incl = r'|'.join([fnmatch.translate(x) for x in includes])
    excl = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'

    allnames = os.listdir(src)
    names = [name for name in allnames if not re.match(excl, name)]

    errors = []

    if not os.path.exists(dst):
        logger.debug('making dir' + str(dst, enc))
        os.makedirs(dst)

    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                if recursive:
                    _copytree(srcname, dstname, excludes, includes, recursive)
                if re.match(incl, name) and recursive:
                    _copytree(srcname, dstname, excludes, includes, recursive)
            elif re.match(incl, name):
                _copy(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise CopyException(errors)


def advanced_copy(src,
                  dst,
                  excludes=[],
                  includes=[],
                  recursive=True,
                  create_directory=True):
    """
    Copy a directory structure src to destination
    
    :param src: source file or directory
    :type src: path
    :param dst: destination file or directory
    :type dst: path
    :param excludes: list of patterns to exclude
    :type excludes: list
    :param includes: list of patterns to include
    :type includes: list
    :param recursive: recursive copy
    :param create_directory: create missing directories
    """
    logger = logging.getLogger(__name__)

    src = text_to_native_str(src)  # not Path because it could have a pattern
    dsts = validators.TypedSet(validators.Path)(
        dst
    )  # not is dir because it might not exist if it s just being created
    includes = validators.TypedSet(text_to_native_str)(includes)
    excludes = validators.TypedSet(text_to_native_str)(excludes)

    # treat case src is given as a pattern and does not really exist,
    # convert it to an include
    if '*' in src:
        src = src.replace('\\', '/')
        bf, af = src.split('*', 1)
        src, inc = bf.rsplit('/', 1)
        inc = '%s*%s' % (inc, af)
        includes.add(inc)
    src = validators.ExistingPath(src)

    for dst in dsts:
        # do we need to create dst directories ?
        parts = dst.parts
        cur = validators.Path(parts[0])
        assert cur.exists(), '%s does not exist' % str(cur)
        for p in parts[1:]:
            cur = cur.joinpath(p)
            if not cur.is_dir():
                if not create_directory:
                    raise NotADirectoryException(
                        _('Use create_directory option.'), cur)
                logger.debug(_('creating directory %s' % cur))
                os.makedirs(text_to_native_str(cur.resolve()))
        if src.is_file():
            logger.debug('_copy(%s,%s)' % (str(src), str(dst)))
            _copy(src, dst)
        else:
            logger.debug('_copytree(%s,%s,...)' % (str(src), str(dst)))
            _copytree(src, dst, excludes, includes, recursive)
