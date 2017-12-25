# -*- coding: utf-8 -*-
""" 
ngofilelist.py

utilities to list files in a directory, or a zip file

author: Cedric ROMAN (roman@numengo.com)
licence: GNU GPLv3

"""
from __future__ import unicode_literals
from builtins import range
from builtins import object

import os
import os.path
from pathlib import Path

def list_files_with_patterns(srcdir,pattern='*',excludes=[],recursive=True):
    """ list files in a source directory with a list of given patterns 
    
    srcdir: source directory
    pattern: pattern or list of patterns ('*.py', '*.txt', etc...)
    excludes: patterns to exclude
    recursive: boolean to explore recursively
    """
    if not isinstance(srcdir,Path):
        srcdir = Path(srcdir)
    if not srcdir.is_dir():
        raise Exception('%s is not a directory'%srcdir)
        
    if isinstance(pattern,list):
        ret = []
        for _ in pattern:
            ret += list_files_with_patterns(srcdir,_,excludes,recursive)
        return ret
    if recursive and not pattern.startswith('**/'):
        pattern = '**/' + pattern
    ms = sorted(srcdir.glob(pattern))
    for pt in excludes:
        ms = [m for m in ms if not m.match(pt)]
    return ms
        
def list_files(srcdir,excludes=[],recursive=False):
    """ list files of a directory with a list of excludes pattern 
    
    srcdir: source directory
    excludes: list of patterns to exclude
    recursive: boolean to list files recursively
    """
    # first we define a helper function for recursive operations
    def list_files_in_dir(srcdir, includes, excludes, recursive):
        import re
        import fnmatch
        ret = []
        if not srcdir.is_dir(): raise Exception('%s is not a directory'%srcdir)
        incl = r'|'.join([fnmatch.translate(x) for x in includes])
        excl = r'|'.join([fnmatch.translate(x) for x in excludes]) or r'$.'
        allnames = [_.name for _ in srcdir.glob('*')]
        names = [name for name in allnames if re.match(excl, name) is None]
        for name in names:
            srcname = srcdir.joinpath(name)
            if srcname.is_dir():
                if re.match(incl, name) and recursive:
                    ret = ret + list_files_in_dir(srcname, includes, excludes,
                                               recursive)
            elif re.match(incl, name):
                ret.append(srcname)
        return ret

    if not isinstance(srcdir,Path):
        srcdir = Path(srcdir)
    if not srcdir.is_dir():
        raise Exception('%s is not a directory'%srcdir)
        
    # now real stuff
    return list_files_in_dir(srcdir, ['*'], excludes,
                               recursive)

def list_files_to_move(srcdir,dest,excludes=[],recursive=False):
    """ list files to move from a directory to another.
    
    srcdir: source directory
    dest: destination directory
    excludes: list of patterns to exclude
    recursive: boolean
    """
    files = list_files(srcdir,excludes,recursive)
    d = Path(dest)
    return [(f, d.joinpath(f.relative_to(srcdir)) )
            for f in files]
        
def list_files_in_zip(archive, pattern, excludes=[], recursive=False):
    """ list files in a zip file

    archive: zipfile object
    pattern: pattern or list of patterns ('*.py', '**/*.py', etc...)
    excludes: list of patterns to exclude
    recursive: boolean
    """
    pattern = pattern.replace('\\','/')
    import re, fnmatch, zipfile
    #if not zipfile.is_zipfile(srczipfile):
    #    raise Exception('%s is not a valid zip file'%srczipfile)
    #a = zipfile.ZipFile(srczipfile,'r')
    dirs = set()
    for d in [
            re.match('(.*)/[^/]*$', l).group(1) for l in archive.namelist()
            if re.match('(.*)/[^/]*$', l)
    ]:
        dirs.add(d)
        for i in range(len(d.split('/'))):
            dirs.add('/'.join(d.split('/')[0:i]))
    incl = fnmatch.translate(pattern)
    #print incl
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

def path_join(pathlist):
    """ join a list of paths and clean it """
    return os.path.sep.join(pathlist).replace('\\\\', '\\')
