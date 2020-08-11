# -*- coding: utf-8 -*-
"""
utilities to list files in a directory, or a zip file

author: Cedric ROMAN (roman@numengo.com)
licence: GNU GPLv3
"""
from __future__ import unicode_literals

import fnmatch
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)


def yield_files(src,
               includes=["*"],
               excludes=[],
               recursive=False,
               in_parents=False,
               folders=0):
    """
    List files in a source path with a list of given patterns

    if src contains patterns, modifies initial source dir and create corresponding includes patterns

    :param src: source directory
    :type src: str
    :param includes: pattern or list of patterns (*.py, *.txt, etc...)
    :type includes: [str,list]
    :param excludes: pattern or patterns to exclude
    :type excludes: [str,list]
    :param recursive: list files recursively
    :param in_parents: list files recursively in parents
    :param folders: 0: without folders, 1: with folders, 2: only folders
    :type folders: enum:[0,1,2]
    :rtype: path
    """
    if type(src) in [list, set, tuple]:
        for s in src:
            for f in list_files(s, includes, excludes, recursive, in_parents,
                                folders):
                yield f
        return

    # declare includes regex and create a function to compile it
    global inclp
    inclp = None

    def _compile_includes(includes):
        global inclp
        incl = r'|'.join([fnmatch.translate(x) for x in includes])
        inclp = re.compile(incl, re.IGNORECASE)

    # declare excludes regex and create a function to compile it
    global exclp
    exclp = None

    def _compile_excludes(excludes):
        global exclp
        excl = r'|'.join([fnmatch.translate(x)
                          for x in excludes]) or r'$.'
        exclp = re.compile(excl, re.IGNORECASE)

    # global counters
    global f_count
    global d_count
    f_count = 0
    d_count = 0

    # first we define a helper function for recursive operations
    def list_files_in_dir(srcdir, includes, excludes, recursive):
        """ we use strings and only create a path object if it s a resut """
        global inclp, exclp
        global d_count
        lf_count = 0  # local file counter
        ld_count = 0  # local inner directory counter
        for p in includes:
            p2 = p.replace('\\', '/')
            if '/' in p2:
                includes2 = set(includes)
                pa, pb = p2.split('/', 1)
                includes2.remove(p)
                includes2.add(pb)
                pa = os.path.join(srcdir, pa)
                if os.path.exists(pa):
                    ld_count += 1
                    _compile_includes(includes2)
                    for f in list_files_in_dir(pa, includes2, excludes,
                                               recursive):
                        lf_count += 1
                        yield f
                    _compile_includes(includes)

        for p in excludes:
            p2 = p.replace('\\', '/')
            if '/' in p2:
                excludes2 = set(excludes)
                pa, pb = p2.split('/', 1)
                excludes2.remove(p)
                excludes2.add(pb)
                pa = os.path.join(srcdir, pa)
                if os.path.exists(pa):
                    ld_count += 1
                    _compile_excludes(excludes2)
                    for f in list_files_in_dir(pa, includes, excludes2,
                                               recursive):
                        lf_count += 1
                        yield f
                    _compile_excludes(excludes)
        names_all = os.listdir(srcdir)
        names_not_excl = [
            name for name in names_all if not exclp.match(name)
        ]
        for name in names_not_excl:
            path = os.path.join(srcdir, name)
            is_dir = os.path.isdir(path)
            if os.path.isdir(path) and recursive:
                for f in list_files_in_dir(path, includes, excludes,
                                           recursive):
                    lf_count += 1
                    yield pathlib.Path(f)
            if inclp.match(name):
                if ((folders == 0 and not is_dir) or (folders == 1)
                        or (folders == 2 and is_dir)):
                    lf_count += 1
                    yield pathlib.Path(path)

        d_count += ld_count
        logger.debug('found %i files in %s (and %i inner directories)',
                     lf_count, srcdir, ld_count)

    src = text_to_native_str(str(src))
    # treat case src is given as a pattern and does not really exist,
    # convert it to an include
    if '*' in src:
        src = src.replace('\\', '/')
        bf, af = src.split('*', 1)
        src, inc = bf.rsplit('/', 1)
        inc = '%s*%s' % (inc, af)
        includes.add(inc)
    if not os.path.exists(src):
        raise IOError('impossible to list file in non existing directory %s',
                      src)
    if not os.path.isdir(src):  # it s a file, returns it
        yield pathlib.Path(src)
        return

    # to compile regexp only when they change
    if not isinstance(includes, list):
        includes = [includes]
    if not isinstance(excludes, list):
        excludes = [excludes]
    # this creates a set of all includes/excludes in native string
    includes = set([text_to_native_str(i) for i in includes])
    excludes = set([text_to_native_str(e) for e in excludes])
    _compile_includes(includes)
    _compile_excludes(excludes)

    for f in list_files_in_dir(src, includes, excludes, recursive):
        f_count += 1
        yield pathlib.Path(f)

    logger.info('found %i files in %s (and %i inner directories)', f_count,
                src, d_count)

    if in_parents:
        srcdir = pathlib.Path(src)
        cur = srcdir.resolve()
        while cur.stem:
            f_count = 0
            d_count = 0
            excludes2 = excludes.union(set([cur.relative_to(cur.parent)]))
            excludes2 = set([text_to_native_str(str(e)) for e in excludes2])
            for f in list_files_in_dir(
                    text_to_native_str(str(cur.parent)), includes, excludes2,
                    recursive):
                f_count += 1
                yield pathlib.Path(f)
            if f_count:
                logger.info(
                    'found %i files in parents in %s (and %i inner directories)',
                    f_count, cur.parent, d_count)
            cur = cur.parent


def list_files(src,
               includes=["*"],
               excludes=[],
               recursive=False,
               in_parents=False,
               folders=0):
    __doc__ = yield_files.__doc__
    return list(yield_files(src, includes, excludes, recursive, in_parents, folders))


def yield_files_in_zip(archive,
                      includes=["*"],
                      excludes=[],
                      recursive=False,
                      directories=True):
    """
    List files in a zip file

    :param archive: zipfile to explore
    :type archive: zipfile.ZipFile
    :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
    :type includes: [str,list]
    :param excludes: patterns to exclude
    :type excludes: [str,list]
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

    for n in archive.namelist():
        if re.match(incl, n) and re.search(excl, n) is None:
            yield n


def list_files_in_zip(archive,
                      includes=["*"],
                      excludes=[],
                      recursive=False,
                      directories=True):
    __doc__ = yield_files_in_zip.__doc__
    return list(yield_files_in_zip(archive, includes, excludes, recursive, directories))
