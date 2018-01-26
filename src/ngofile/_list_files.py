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

from ._assert_path import assert_Path
from .exceptions import NotADirectoryException
from .exceptions import NotAZipArchiveException
from .exceptions import NotExistingPathException

_ = gettext.gettext


def list_files(srcdir,
               includes=["*"],
               excludes=[],
               recursive=False,
               in_parents=False):
    """ list files in a source directory with a list of given patterns 
    
    :param srcdir: source directory
    :type srcdir: str/pathlib.Path
    :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
    :type includes: str/list
    :param excludes: pattern or patterns to exclude
    :type excludes: str/list
    :param recursive:list files recursively
    :param in_parents: list files recursively in parents
    :rtype: ngomodel.TypedList(pathlib.Path)
    """
    logger = logging.getLogger(__name__)

    # first we define a helper function for recursive operations
    def list_files_in_dir(srcdir, includes, excludes, recursive):
        ret = []
        for p in includes:
            includes2 = includes
            p2 = p.replace('\\', '/')
            if '/' in p2:
                pa, pb = p2.lsplit('/', 1)
                includes2.pop(p)
                includes2.append(pb)
                if srcdir.joinpath(pa).exists():
                    ls = list_files_in_dir(
                        srcdir.joinpath(pa), includes2, excludes, recursive)
                    ret += ls
        for p in excludes:
            excludes2 = excludes
            p2 = p.replace('\\', '/')
            if '/' in p2:
                pa, pb = p2.lsplit('/', 1)
                excludes2.pop(p)
                excludes2.append(pb)
                if srcdir.joinpath(pa).exists():
                    ls = list_files_in_dir(
                        srcdir.joinpath(pa), includes, excludes2, recursive)
                    ret += ls
        srcdir = assert_Path(srcdir)
        if isinstance(srcdir, list):
            return [
                list_files_in_dir(s, includes, excludes, recursive)
                for s in srcdir
            ]
        if not srcdir.is_dir():
            raise NotADirectoryException('', srcdir)
        incl = r'|'.join([fnmatch.translate(x.lower()) for x in includes])
        excl = r'|'.join([fnmatch.translate(x.lower())
                          for x in excludes]) or r'$.'
        names_all = os.listdir(srcdir.__str__())
        #names_all = os.listdir(str(srcdir))
        #names_all2 = [n.name for n in srcdir.glob('*')]
        names_not_excl = [
            name for name in names_all if re.match(excl, name.lower()) is None
        ]
        for name in names_not_excl:
            path = srcdir.joinpath(name)
            if path.is_dir() and recursive:
                ret = ret + list_files_in_dir(path, includes, excludes,
                                              recursive)
            elif re.match(incl, name):
                ret.append(path)
        logger.debug(_('found %(n)d files' % {'n': len(ret)}))
        return ret

    srcdir = assert_Path(srcdir)
    if not srcdir.exists():
        return []
    if not isinstance(includes, list):
        includes = [includes]
    if not isinstance(excludes, list):
        excludes = [excludes]
    ret = list_files_in_dir(srcdir, includes, excludes, recursive)
    if in_parents:
        cur = srcdir.resolve()
        while cur.stem:
            ret += list_files_in_dir(
                cur.parent, includes,
                excludes + [str(cur.relative_to(cur.parent))], recursive)
            cur = cur.parent
        return ret
    return ret


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


def list_files_in_zip(archive, includes=["*"], excludes=[], recursive=False):
    """ list files in a zip file

    :param archive: zipfile to explore
    :type archive: zipfile.ZipFile
    :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
    :type includes: str/list
    :param excludes: patterns to exclude
    :type excludes: str/list
    :param recursive: list files recursively
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
