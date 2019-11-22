# coding: utf-8
""" 
Misc copy utilities
"""
from __future__ import unicode_literals

import filecmp
import fnmatch
import logging
import os
import os.path
import re
import shutil
import sys
from builtins import str
from pathlib import Path

from future.utils import text_to_native_str

from . import get_unicode
from .exceptions import CopyException
from .exceptions import NgoFileException
from .exceptions import NotADirectoryException
from .exceptions import NotExistingPathException

enc = sys.stdout.encoding or "cp850"


def _copy(src, dst):
    """
    Copy a file src to dst (directory).
    
    If dst exists and is the same, nothing is done

    :param src: source file or directory
    :type src: path
    :param dst: destination file or directory
    :type dst: path
    """
    logger = logging.getLogger(__name__)
    src = text_to_native_str(src)
    dst = text_to_native_str(dst)
    if os.path.exists(dst) and os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.exists(dst):
        if not filecmp.cmp(src, dst):
            logger.debug('updating %s', get_unicode(dst, enc))
            shutil.copy2(src, dst)
        else:
            logger.debug('%s already up to date', get_unicode(dst, enc))
    else:
        logger.debug('copy %s to %s', get_unicode(src, enc),
                     get_unicode(dst, enc))
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
    src = text_to_native_str(str(src))
    dst = text_to_native_str(str(dst))

    incl = r'|'.join([fnmatch.translate(x) for x in includes])
    excl = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'

    allnames = os.listdir(src)
    names = [name for name in allnames if not re.match(excl, name)]

    errors = []

    if not os.path.exists(dst):
        logger.debug('making dir %s', get_unicode(dst, enc))
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
    :type src: string
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
    dsts = dst if isinstance(dst, list) else [dst]
    dsts = [Path(text_to_native_str(f)) for f in dsts]
    # not is dir because it might not exist if it s just being created
    includes = includes if isinstance(includes, list) else [includes]
    excludes = excludes if isinstance(excludes, list) else [excludes]
    includes = set([text_to_native_str(i) for i in includes])
    excludes = set([text_to_native_str(e) for e in excludes])
    # treat case src is given as a pattern and does not really exist,
    # convert it to an include
    src = text_to_native_str(str(src))
    if '*' in src:
        src = src.replace('\\', '/')
        bf, af = src.split('*', 1)
        src, inc = bf.rsplit('/', 1)
        inc = '%s*%s' % (inc, af)
        includes.add(inc)

    src = Path(src)
    assert src.exists()

    for dst in dsts:
        # do we need to create dst directories ?
        parts = dst.parts
        cur = Path(parts[0])
        assert cur.exists(), '%s does not exist' % get_unicode(cur)
        for p in parts[1:]:
            cur = cur.joinpath(p)
            if not cur.is_dir():
                if not create_directory:
                    raise NotADirectoryException(
                        'Use create_directory option.', cur)
                logger.debug('creating directory %s', cur)
                os.makedirs(text_to_native_str(str(cur.resolve())))
        if src.is_file():
            logger.debug('_copy(%s,%s)', get_unicode(str(src), enc),
                         get_unicode(str(dst), enc))
            _copy(src, dst)
        else:
            logger.debug('_copytree(%s,%s,...)', get_unicode(str(src), enc),
                         get_unicode(str(dst), enc))
            _copytree(src, dst, excludes, includes, recursive)
