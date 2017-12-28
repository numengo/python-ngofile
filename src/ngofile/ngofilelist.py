# -*- coding: utf-8 -*-
""" 
ngofilelist.py

utilities to list files in a directory, or a zip file

author: Cedric ROMAN (roman@numengo.com)
licence: GNU GPLv3
"""
from __future__ import unicode_literals

from builtins import str
import fnmatch
import re
import zipfile
from builtins import range
from pathlib import Path

from .exceptions import NotExistingPathException, NotADirectoryException, NotAZipArchiveException

try:
    unicode = str
except Exception:
    pass


def _assert_is_directory(path):
    """ asserts a path exists and is a directory or throw exception

    :param path: path to assert
    :type path: string or pathlib.Path
    :rtype: pathlib.Path """
    if not isinstance(path, Path):
        path = Path(str(path))
    if not path.exists():
        raise NotExistingPathException("%s does not exist." % path)
    if not path.is_dir():
        raise NotADirectoryException("%s is not a directory" % path)
    return path


def list_files(srcdir, includes=["*"], excludes=[], recursive=False):
    """ list files in a source directory with a list of given patterns 
    
    :param srcdir: source directory
    :type srcdir: string or pathlib.Path
    :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
    :type includes: string or list of strings
    :param excludes: patterns to exclude
    :type excludes: string or list of strings
    :param recursive:list files recursively
    :type recursive: boolean
    :rtype: list of pathlib.Path
    """

    # first we define a helper function for recursive operations
    def list_files_in_dir(srcdir, includes, excludes, recursive):
        ret = []
        if not srcdir.is_dir():
            raise NotADirectoryException('%s is not a directory' % srcdir)
        incl = r'|'.join([fnmatch.translate(x) for x in includes])
        excl = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'
        names_all = [_.name for _ in srcdir.glob('*')]
        names_not_excl = [
            name for name in names_all if re.match(excl, name) is None
        ]
        for name in names_not_excl:
            path = srcdir.joinpath(name)
            if path.is_dir() and recursive:
                ret = ret + list_files_in_dir(path, includes, excludes,
                                              recursive)
            elif re.match(incl, name):
                ret.append(path)
        return ret

    srcdir = _assert_is_directory(srcdir)
    if not isinstance(includes, list):
        includes = [includes]
    return list_files_in_dir(srcdir, includes, excludes, recursive)


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
    :type includes: string or list of strings
    :param excludes: patterns to exclude
    :type excludes: string or list of strings
    :param recursive:list files recursively
    :type recursive: boolean
    :rtype: list of strings
    """
    if not isinstance(includes, list):
        includes = [includes]
    includes = [i.replace('\\', '/') for i in includes]
    if not isinstance(archive, zipfile.ZipFile):
        raise NotAZipArchiveException(
            '%r is not a valid zip file' % archive)
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
