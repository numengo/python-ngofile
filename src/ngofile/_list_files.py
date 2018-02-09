# -*- coding: utf-8 -*-
""" 
_list_files.py

utilities to list files in a directory, or a zip file

author: Cedric ROMAN (roman@numengo.com)
licence: GNU GPLv3
"""
from __future__ import unicode_literals

import fnmatch
import gettext
import logging
import os
import os.path
import pathlib
import re
import zipfile
from builtins import range
from builtins import str

from future.utils import text_to_native_str

from .exceptions import NotADirectoryException
from .exceptions import NotAZipArchiveException
from .exceptions import NotExistingPathException

_ = gettext.gettext


def list_files(src,
               includes=["*"],
               excludes=[],
               recursive=False,
               in_parents=False,
               directories=True,
               raise_src_exists=True):
    """ list files in a source path with a list of given patterns

    if src contains patterns, modifies initial source dir and create corresponding includes patterns
    
    :param src: source directory
    :type src: str
    :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
    :type includes: str/list
    :param excludes: pattern or patterns to exclude
    :type excludes: str/list
    :param recursive: list files recursively
    :param in_parents: list files recursively in parents
    :param directories: list also directories
    :param raise_src_exists: raise exception if src does not exist, or return empty list
    :rtype: pathlib.Path
    """
    logger = logging.getLogger(__name__)
    if type(src) in [list, set, tuple]:
        return [
            list_files(s, includes, excludes, recursive, in_parents,
                       directories, raise_src_exists) for s in src
        ]

    # declare includes regex and create a function to compile it
    global inclp
    inclp = None

    def _compile_includes(includes):
        global inclp
        incl = r'|'.join([fnmatch.translate(x.lower()) for x in includes])
        inclp = re.compile(incl)

    # declare excludes regex and create a function to compile it
    global exclp
    exclp = None

    def _compile_excludes(excludes):
        global exclp
        excl = r'|'.join([fnmatch.translate(x.lower())
                          for x in excludes]) or r'$.'
        exclp = re.compile(excl)

    global count
    count = 0  # global counter

    # first we define a helper function for recursive operations
    def list_files_in_dir(srcdir, includes, excludes, recursive):
        """ we use strings and only create a path object if it s a resut """
        global inclp, exclp
        global count
        ret = []
        count += 1
        count2 = 0  # local counter
        for p in includes:
            p2 = p.replace('\\', '/')
            if '/' in p2:
                includes2 = set(includes)
                pa, pb = p2.split('/', 1)
                includes2.remove(p)
                includes2.add(pb)
                pa = os.path.join(srcdir, pa)
                if os.path.exists(pa):
                    count2 += 1
                    _compile_includes(includes2)
                    ls = list_files_in_dir(pa, includes2, excludes, recursive)
                    _compile_includes(includes)
                    ret += ls

        for p in excludes:
            p2 = p.replace('\\', '/')
            if '/' in p2:
                excludes2 = set(excludes)
                pa, pb = p2.split('/', 1)
                excludes2.remove(p)
                excludes2.add(pb)
                pa = os.path.join(srcdir, pa)
                if os.path.exists(pa):
                    count2 += 1
                    _compile_excludes(excludes2)
                    ls = list_files_in_dir(pa, includes, excludes2, recursive)
                    _compile_excludes(excludes)
                    ret += ls
        names_all = os.listdir(srcdir)
        names_not_excl = [
            name for name in names_all if not exclp.match(name.lower())
        ]
        for name in names_not_excl:
            path = os.path.join(srcdir, name)
            if os.path.isdir(path) and recursive:
                ret += list_files_in_dir(path, includes, excludes, recursive)
            if inclp.match(name.lower()):
                if directories or path.is_dir():
                    ret.append(pathlib.Path(path))
        if ret:
            logger.debug(
                _('found %i files in %s (and %i inner directories)' %
                  (len(ret), srcdir, count2)))
        else:
            logger.debug(
                _('no files found in %s (and %i inner directories)' %
                  (srcdir, count2)))
        return ret

    src = text_to_native_str(src)
    # treat case src is given as a pattern and does not really exist,
    # convert it to an include
    if '*' in src:
        src = src.replace('\\', '/')
        bf, af = src.split('*', 1)
        src, inc = bf.rsplit('/', 1)
        inc = '%s*%s' % (inc, af)
        includes.add(inc)
    if not os.path.exists(src):
        if raise_src_exists:
            raise IOError(
                _('impossible to list file in non existing directory %s' %
                  src))
        return []
    if not os.path.isdir(src):  # it s a file, returns it
        return [src]

    # to compile regexp only when they change
    if not isinstance(includes, list):
        includes = [includes]
    if not isinstance(excludes, list):
        includes = [excludes]
    # this creates a set of all includes/excludes in native string
    includes = set([text_to_native_str(i) for i in includes])
    excludes = set([text_to_native_str(e) for e in excludes])
    _compile_includes(includes)
    _compile_excludes(excludes)

    ret = list_files_in_dir(src, includes, excludes, recursive)
    logger.debug(
        _('found %i files in %s (and %i inner directories)' % (len(ret), src,
                                                               count)))

    if in_parents:
        srcdir = pathlib.Path(src)
        cur = srcdir.resolve()
        while cur.stem:
            count = 0
            inpar = list_files_in_dir(
                cur.parent, includes,
                excludes + set([cur.relative_to(cur.parent)]), recursive)
            if inpar:
                logger.debug(
                    _('found %i files in parents in %s (and %i inner directories)'
                      % (len(inpar), cur.parent, count)))
            ret += inpar
            cur = cur.parent
    return ret


def list_files_in_zip(archive,
                      includes=["*"],
                      excludes=[],
                      recursive=False,
                      directories=True):
    """ list files in a zip file

    :param archive: zipfile to explore
    :type archive: zipfile.ZipFile
    :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
    :type includes: str/list
    :param excludes: patterns to exclude
    :type excludes: str/list
    :param recursive: list files recursively
    :param directories: list also directories (NOT IMPLEMENTED)
    :rtype: list
    """
    if not isinstance(includes, list):
        includes = [includes]
    includes = [i.replace('\\', '/') for i in includes]
    if not isinstance(archive, zipfile.ZipFile):
        raise NotAZipArchiveException('%r is not a valid zip file' % archive)
    dirs = set()
    for d in [
            re.match('(.*)/[^/]*$', l).group(1) for l in archive.namelist()
            if re.match('(.*)/[^/]*$', l)
    ]:
        dirs.add(d)
        for i in range(len(d.split('/'))):
            dirs.add('/'.join(d.split('/')[0:i]))
    incl = r'|'.join([fnmatch.translate(x) for x in includes])
    excl = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'
    if len([x for x in dirs if re.match(incl, x)]):
        incl = incl.replace(
            '\Z(?ms)', r'\/.*\Z(?ms)'
        )  #http://stackoverflow.com/questions/11998613/regular-expression-zms
        incl = incl.replace('$', r'\/.*$')
    if not recursive:
        incl = incl.replace('.*\Z(?ms)', r'[^/]*\Z(?ms)')
        incl = incl.replace('.*$', r'[^/]*$')
    return [
        n for n in archive.namelist()
        if re.match(incl, n) and re.search(excl, n) is None
    ]
