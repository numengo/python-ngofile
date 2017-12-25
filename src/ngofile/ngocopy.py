# coding: utf-8
""" misc copy utilities
"""

from builtins import str
from builtins import range
import fnmatch
import os
import os.path
import re
import filecmp
import shutil
import logging

import sys
enc = sys.stdout.encoding or "cp850"


def ngocopy(src, dst):
    """ copy a file src to dst (directory). 
    
    if dst exists and is the same, nothing is done"""
    logger = logging.getLogger(__name__)
    if os.path.exists(dst) and os.path.isdir(dst):
        dst = os.path.join(dst, os.path.basename(src))
    if os.path.exists(dst):
        if not filecmp.cmp(src, dst):
            logger.debug('updating ' + str(dst, enc))
            shutil.copy2(src, dst)
        else:
            pass
            #logger.info(unicode(dst,enc) + ' already up to date')
    else:
        logger.debug('copy ' + str(src, enc) + ' to ' + str(dst, enc))
        shutil.copy2(src, dst)


def ngocopytree(src, dst, excludes=[], includes=[], recursive=True):
    """ copy a directory structure src to destination
    
    excludes: is a list of pattern files to exclude
    includes: is a list of pattern file to include
    recursive: option for recursive copy (default is true)
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
                    ngocopytree(srcname, dstname, excludes, includes,
                                recursive)
                if re.match(incl, name) and recursive:
                    ngocopytree(srcname, dstname, excludes, includes,
                                recursive)
            elif re.match(incl, name):
                ngocopy(srcname, dstname)
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


def advanced_copy(src, dst, excludes=[], includes=[], recursive=True):
    """
    copy src to destination.  frontent to deal with all cases (src file or directory)
    
    excludes: is a list of pattern files to exclude
    includes: is a list of pattern file to include
    recursive: option for recursive copy (default is true)
    """
    logger = logging.getLogger(__name__)
    # make sure to convert string from ngopath
    # convert everything to ngopath and back to string
    if not os.path.isdir(src) and not os.path.isfile(src):
        if os.path.isdir(os.path.dirname(src)):
            includes = [os.path.basename(src)]
            recursive = False
            src = os.path.dirname(src)
    if not os.path.exists(src):
        logger.error('source  ' + src + ' does not exist')
        return

    # do we need to create dst directories ?
    dirs = dst.split(os.path.sep)
    for i in range(len(dirs)):
        d = os.path.sep.join(dirs[:i + 1])
        if not os.path.exists(d):
            logger.debug('creating directory ' + str(d, enc))
            os.makedirs(d)

    if os.path.isfile(src):
        ngocopy(src, dst)
    else:
        ngocopytree(src, dst, excludes, includes, recursive)
