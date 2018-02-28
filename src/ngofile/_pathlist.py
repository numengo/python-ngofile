# coding: utf-8
"""
2017/11/12: C.ROMAN (in africa)
functions/class to deal with filepathes
"""
from __future__ import unicode_literals

import inspect
import logging
import operator
import os.path
import pathlib
import pprint
import sys
from builtins import object
from builtins import str

from future.utils import text_to_native_str

from ._list_files import list_files


class PathList(object):
    """ path list manager """
    _initialized = False
    _instance = None
    _pathdict = {
    }  # we store the pathlist as a dict to store last search results

    def __new__(cls, *args, **kwargs):
        singleton = kwargs.get('singleton', True)
        if singleton:
            if not cls._instance:
                cls._instance = super(PathList, cls).__new__(cls)
                cls._instance._pathdict = {}
            return cls._instance
        else:
            cls._pathdict = {}
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

    def __str__(self):
        return ("<%s>\n%s" % (self.__class__.__name__,
                              pprint.pformat(list(self.pathlist))))

    def __repr__(self):
        '''Returns representation of the object'''
        return ("<%s[%i items]>" % (self.__class__.__name__,
                                    len(self._pathdict)))

    @property
    def pathlist(self):
        return set(self._pathdict.keys())

    @pathlist.setter
    def pathlist(self, pathlist):
        """ set the pathlist from a list
        :param pathlist: path list to set
        :rtype pathlist: list"""
        self._pathdict.clear()
        for p in pathlist:
            self.add(p)

    def as_strings(self):
        """ returns the pathlist as a set of string
        :rtype: set"""
        return set([text_to_native_str(p) for p in self.pathlist])

    def add(self, path):
        """ append a path to pathlist (only if it exists)

        :param path: path to assert
        :type path: pathlib.Path """
        if type(path) in [list, set, tuple]:
            return [self.exists(p) for p in path]
        p = text_to_native_str(path)
        if '*' in p:
            # use list_files to create a list of files coressponding to pattern
            # and add the list pathlist
            self.add(list_files(p))
        p = pathlib.Path(path)
        if p not in self.pathlist:
            if p.exists():
                p = p.resolve()
                self._pathdict[p] = 0  # intialize counter
            else:
                self.logger.warning('%s does not exist' % p)

    def exists(self, path):
        """ check if a path exists in pathlist

        :param path: path or pattern
        :type path: pathlib.Path
        :rtype: bool"""
        if type(path) in [list, set, tuple]:
            return [self.exists(p) for p in path]
        return bool(self.pick_first(path))

    def pick_first(self, path):
        """ pick the first existing match

        :param path: path or pattern
        :type path: str
        :rtype: pathlib.Path """
        if type(path) in [list, set, tuple]:
            return [self.pick_first(p) for p in path]
        path = text_to_native_str(path)
        path = path.replace('\\', '/')
        includes = []
        if '*' in path:
            bf, af = path.split('*', 1)
            path, inc = bf.rsplit('/', 1)
            includes = ['%s*%s' % (inc, af)]
        if os.path.exists(path):
            return pathlib.Path(path)
        optimized_pathlist = sorted(
            list(self._pathdict.items()),
            key=operator.itemgetter(1),
            reverse=True)
        for p, _oldc in optimized_pathlist:
            if p.joinpath(path).exists():
                ls = list_files(p.joinpath(path), includes)
                # we dont update the counter because all paths are not treated equally
                #self._pathdict[p] = len(ls)
                if ls:
                    return ls[0]

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
        :rtype: ngomodel.validators.TypedList(pathlib.Path)
        """
        ret = [None] * len(self._pathdict)
        optimized_pathlist = sorted(
            list(self._pathdict.items()),
            key=operator.itemgetter(1),
            reverse=True)
        for p, _oldc in optimized_pathlist:
            ls = list_files(p, includes, excludes, recursive, in_parents)
            self._pathdict[p] = len(ls)
            ret[list(self.pathlist).index(p)] = ls

        if flatten:
            return [item for sublist in ret for item in sublist]

        return ret


class LoadedModules(PathList):
    """ special pathlist of loaded modules directories """

    def __init__(self):
        PathList.__init__(self, singleton=True)
        if not self._initialized:
            self._initialized = True
            self.update()

    def _get_current_pathset(self):
        """ method to create set of path of currently loaded modules """
        ms = { k: m for k, m in list(sys.modules.items())
              if m and inspect.ismodule(m) and not inspect.isbuiltin(m) and not k.startswith('_')}
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
        ret = PathList.list_files(self, includes, excludes, recursive,
                                  in_parents)
        if not ret:
            s1 = self.pathlist
            s2 = self._get_current_pathset()
            df = s2.difference(s1)
            if df:
                self.update()
                return PathList.list_files(self, includes, excludes, recursive,
                                           in_parents)
        return ret


def list_all_dirs_in_modules(template):
    return LoadedModules().list_files(template)
