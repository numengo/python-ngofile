# coding: utf-8
""" misc copy utilities
"""
from __future__ import unicode_literals

import filecmp
import fnmatch
import logging
import os
import os.path
from pathlib import Path
import re
import shutil
import sys
import gettext
from builtins import range
from builtins import str

from .exceptions import NgoFileException, NotExistingPathException, NotADirectoryException
from ._assert_path import assert_Path

enc = sys.stdout.encoding or "cp850"
_ = gettext.gettext


def _copy(src, dst):
    """ copy a file src to dst (directory).
    
    if dst exists and is the same, nothing is done

    :param src: source file or directory
    :type src: pathlib.Path
    :param dst: destination file or directory
    :type dst: pathlib.Path
    """
    logger = logging.getLogger(__name__)
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
    """ copy a directory structure src to destination
    
    :param src: source file or directory
    :type src: pathlib.Path
    :param dst: destination file or directory
    :type dst: pathlib.Path
    :param excludes: list of patterns to exclude
    :type excludes: list
    :param includes: list of patterns to include
    :type includes: list
    :param recursive: recursive copy
    """
    logger = logging.getLogger(__name__)
    # make sure to convert string from ngopath
    # convert everything to ngopath and back to string

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
                    _copytree(srcname, dstname, excludes, includes,
                                recursive)
                if re.match(incl, name) and recursive:
                    _copytree(srcname, dstname, excludes, includes,
                                recursive)
            elif re.match(incl, name):
                _copy(srcname, dstname)
        except (IOError, os.error) as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
        pass
    except WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError as why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise Exception(errors)


def advanced_copy(src, dst, excludes=[], includes=[], recursive=True,create_directory=True):
    """ copy a directory structure src to destination
    
    :param src: source file or directory
    :type src: pathlib.Path
    :param dst: destination file or directory
    :type dst: pathlib.Path
    :param excludes: list of patterns to exclude
    :type excludes: list
    :param includes: list of patterns to include
    :type includes: list
    :param recursive: recursive copy
    :param create_directory: create missing directories
    """
    logger = logging.getLogger(__name__)
    
    src = assert_Path(src) # not flag exits because it could have a pattern
    dst = assert_Path(dst) # not is dir because it might not exist if it s just being created
    
    for d in dst:
        for s in src:
            advanced_copy(s, d, excludes, includes, recursive)
            
    # treat case src is given as a pattern and does not really exist, 
    # convert it to an include
    if not src.is_dir() and not src.exists():
        if src.parent.is_dir():
            includes = [src.name] # append ??
            recursive=False
            src = src.parent
    if not src.exists():
        e = NotExistingPathException('',src)
        logger.error(e)
        return

    # do we need to create dst directories ?
    parts = dst.parts
    cur = Path(parts[0])
    assert cur.exists(), '%s does not exist' % str(cur, enc)
    for p in parts[1:]:
        cur = cur.joinpath(p)
        if not cur.exists():
            if not create_directory:
                e= NotADirectoryException(_('Use create_directory option.'),cur)
                logger.exception(e)
                raise e
            logger.debug(_('creating directory ')+str(cur, enc))
            os.makedirs(str(cur.resolve()))

    if src.is_file():
        logger.debug('_copy(%s,%s)'%(str(src),str(dst)))
        _copy(src, dst)
    else:
        logger.debug('_copytree(%s,%s,...)'%(str(src),str(dst)))
        _copytree(src, dst, excludes, includes, recursive)
