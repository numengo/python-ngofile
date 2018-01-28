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
import re
import zipfile
from builtins import range
from builtins import str
from pathlib import Path
from future.utils import text_to_native_str
from ngomodel import validators
from ngomodel import take_arrays

from .exceptions import NotADirectoryException
from .exceptions import NotAZipArchiveException
from .exceptions import NotExistingPathException

_ = gettext.gettext

take_arrays(1)
def list_files(src,
               includes=["*"],
               excludes=[],
               recursive=False,
               in_parents=False,
               directories=True):
    """ list files in a source path with a list of given patterns

    if src contains patterns, modifies initial source dir and create corresponding includes patterns
    
    :param srcdir: source directory
    :type srcdir: str/pathlib.Path
    :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
    :type includes: str/list
    :param excludes: pattern or patterns to exclude
    :type excludes: str/list
    :param recursive:list files recursively
    :param in_parents: list files recursively in parents
    :param directories: list also directories
    :rtype: ngomodel.TypedList(pathlib.Path)
    """
    logger = logging.getLogger(__name__)

    inclp = None
    def _compile_includes(includes):
        global inclp
        incl = r'|'.join([fnmatch.translate(x.lower()) for x in includes])
        inclp = re.compile(incl)

    exclp = None
    def _compile_excludes(excludes):
        global exclp
        excl = r'|'.join([fnmatch.translate(x.lower())
                          for x in excludes]) or r'$.'
        exclp = re.compile(excl)

    # first we define a helper function for recursive operations
    def list_files_in_dir(srcdir, includes, excludes, recursive):
        ret = []
        global inclp, exclp
        for p in includes:
            includes2 = includes
            p2 = p.replace('\\', '/')
            if '/' in p2:
                pa, pb = p2.split('/', 1)
                includes2.remove(p)
                includes2.add(pb)
                _compile_includes(includes2)
                if srcdir.joinpath(pa).exists():
                    ls = list_files_in_dir(
                        srcdir.joinpath(pa), includes2, excludes, recursive)
                    ret += ls
        for p in excludes:
            excludes2 = excludes
            p2 = p.replace('\\', '/')
            if '/' in p2:
                pa, pb = p2.lsplit('/', 1)
                excludes2.remove(p)
                excludes2.add(pb)
                _compile_excludes(excludes2)
                if srcdir.joinpath(pa).exists():
                    ls = list_files_in_dir(
                        srcdir.joinpath(pa), includes, excludes2, recursive)
                    ret += ls
        srcdir = validators.DirPath(srcdir)
        incl = r'|'.join([fnmatch.translate(x.lower()) for x in includes])
        excl = r'|'.join([fnmatch.translate(x.lower())
                          for x in excludes]) or r'$.'

        sd = text_to_native_str(srcdir)
        try:
            names_all = os.listdir(sd)
        except Exception as er:
            logger.exception(er)
            return []
        names_not_excl = [
            name for name in names_all if not exclp.match(name.lower())
        ]
        for name in names_not_excl:
            path = srcdir.joinpath(name)
            if path.is_dir() and recursive:
                ret = ret + list_files_in_dir(path, includes, excludes,
                                              recursive)
            elif inclp.match(name.lower()):
                if directories or path.is_dir():
                    ret.append(path)
        if ret:
            logger.debug(_('found %i files in %s' % (len(ret),srcdir)))
        return ret

    if not isinstance(includes,list):
        includes = [includes]
    if not isinstance(excludes,list):
        includes = [excludes]

    src = text_to_native_str(src)  # not Path because it could have a pattern
    # this creates a set of all includes/excludes in native string
    includes = validators.TypedSet(text_to_native_str)(includes)
    excludes = validators.TypedSet(text_to_native_str)(excludes)

    # treat case src is given as a pattern and does not really exist,
    # convert it to an include
    if '*' in src:
        src = src.replace('\\','/')
        bf, af = src.split('*',1)
        src, inc = bf.rsplit('/',1)
        inc = '%s*%s'%(inc,af)
        includes.add(inc)

    srcdir = validators.Path(src)
    if not srcdir.exists():
        return []

    # to compile regexp only when they change
    _compile_includes(includes)
    _compile_excludes(excludes)

    ret = list_files_in_dir(srcdir, includes, excludes, recursive)
    logger.debug(_('found %i files in %s' % (len(ret),srcdir)))

    if in_parents:
        cur = srcdir.resolve()
        while cur.stem:
            inpar = list_files_in_dir(
                cur.parent, includes,
                excludes + set([cur.relative_to(cur.parent)]), recursive)
            if inpar:
                logger.debug(_('found %i files in parents in %s' % (len(inpar),cur.parent)))
            ret += inpar
            cur = cur.parent
    return ret


take_arrays(1)
#def list_files_to_move(srcdir,dest,excludes=[],recursive=False):
#    """ list files to move from a directory to another.
#
#    srcdir: source directory
#    dest: destination directory
#    excludes: list of patterns to exclude
#    recursive: boolean
#    """
#    files = list_files(srcdir,excludes,recursive)
#    d = Path(dest)
#    return [(f, d.joinpath(f.relative_to(srcdir)) )
#            for f in files]


def list_files_in_zip(archive, includes=["*"], excludes=[], recursive=False, directories=True):
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
