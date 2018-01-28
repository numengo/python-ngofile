# coding: utf-8
"""
2017/11/12: C.ROMAN (in africa)
functions/class to deal with filepathes
"""
from __future__ import unicode_literals

import logging
from builtins import object
from builtins import str
import sys
import inspect
import pathlib
from future.utils import text_to_native_str

from ._list_files import list_files
from ngomodel import validators
from ngomodel import take_arrays


class PathList(object):
    """ path list manager """
    _initialized = False
    _instance = None
    _pathlist = set()

    def __new__(cls, *args, **kwargs):
        singleton =  kwargs.get('singleton', True)
        if singleton:
            if not cls._instance:
                cls._instance = super(PathList, cls).__new__(cls)
                cls._instance._pathlist = set()
            return cls._instance
        else:
            cls._pathlist = set()
            return super(PathList, cls).__new__(cls)

    def __init__(self, *args, **kwargs):
        """ appends each arg as a path of pathlist
        if `pathlist` is given as keyword argument used as pathlist."""
        self.logger = logging.getLogger(__name__)
        for arg in args:
            if arg:
                self.add(arg)
        if 'pathlist' in kwargs:
            self.pathlist = kwargs.pop('pathlist')

    def __repr__(self):
        '''Returns representation of the object'''
        return ("{}[{}]('{}')".format(self.__class__.__name__,
                                      len(self._pathlist), self._pathlist))

    @property
    def pathlist(self):
        return self._pathlist

    @pathlist.setter
    def pathlist(self, pathlist):
        """ set the pathlist from a list
        :param pathlist: path list to set
        :rtype pathlist: list"""
        self._pathlist.clear()
        for p in pathlist:
            self.add(p)

    def as_strings(self):
        """ returns the pathlist as a set of string
        :rtype: set"""
        return set([text_to_native_str(p) for p in self._pathlist])

    @take_arrays(1)
    def add(self, path):
        """ append a path to pathlist (only if it exists)

        :param path: path to assert
        :type path: ngomodel.Path """
        p = text_to_native_str(path)
        if '*' in p:
            # use list_files to create a list of files coressponding to pattern
            # and add the list pathlist
            self.add(list_files(p))
        p = validators.Path(path)
        if not p in self.pathlist:
            if p.exists():
                self._pathlist.add(p.resolve())
            else:
                self.logger.warning('%s does not exist' % p)
        else:
            self.logger.warning('%s already in pathlist' % p)

    @take_arrays(1)
    def exists(self, path):
        """ check if a path exists in pathlist

        :param path: path or pattern
        :type path: ngomodel.Path
        :rtype: bool"""
        return len(self.list_files(path)) > 0

    @take_arrays(1)
    def pick_first(self, path):
        """ picks the first existing match

        :param path: path or pattern
        :type path: ngomodel.Path
        :rtype: pathlib.Path/None """
        ms = self.list_files(path)
        if len(ms) > 0:
            return ms[0]

    def list_files(self,
                   includes=["*"],
                   excludes=[],
                   recursive=False,
                   in_parents=False,
                   flatten=True):
        """ list files in a source directory with a list of given patterns 
        
        :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
        :type includes: str/list
        :param excludes: patterns to exclude
        :type excludes: str/list
        :param recursive:list files recursively
        :param in_parents: list files recursively in parents
        :param flatten: flatten return lists
        :rtype: ngomodel.TypedList(pathlib.Path)
        """
        ret = []
        for p in self.pathlist:
            ls = list_files(p, includes, excludes, recursive, in_parents)
            if flatten:
                ret += ls
            else:
                ret.append(ls)
        return ret

class LoadedModules(PathList):
    """ special pathlist of loaded modules directories """
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            self.update()

    def _get_current_pathset(self):
        """ method to create set of path of currently loaded modules """
        ms = {
            k: m
            for k, m in list(sys.modules.items()) if m and inspect.ismodule(m)
            and not inspect.isbuiltin(m) and not k.startswith('_')
        }
        ps = set([
            pathlib.Path(m.__file__).parent for m in list(ms.values())
            if getattr(m, '__file__', None)
        ])
        return ps

    def update(self):
        """ update pathlist from loaded modules """
        self.pathlist = self._get_current_pathset()

    def list_files(self,
                   includes=["*"],
                   excludes=[],
                   recursive=False,
                   in_parents=False,
                   flatten=True):
        """ overloaded method to reload pathlist if no result found """
        ret = PathList.list_files(self,includes,excludes,recursive,in_parents)
        if not ret:
            s1 = self.pathlist
            s2 = self._get_current_pathset()
            df = s2.difference(s1)
            if df:
                self.update()
                return PathList.list_files(self,includes,excludes,recursive,in_parents)
        return ret


def list_all_dirs_in_modules(template):
    return LoadedModules().list_files(template)
