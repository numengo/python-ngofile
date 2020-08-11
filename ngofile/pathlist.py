# coding: utf-8
"""
functions/class to deal with filepaths
"""
from __future__ import unicode_literals

import importlib
import logging
import operator
import os.path
import pathlib
import pprint
from builtins import object
from builtins import str

from future.utils import text_to_native_str

from .list_files import list_files
from .list_files import yield_files


class PathList(object):
    """
    Pathlist manager
    """
    _logger = logging.getLogger(__name__)

    def __init__(self, *args, **kwargs):
        """
        Appends each arg as a path of pathlist
        """
        self._pathdict = {}
        for arg in args:
            self.add(arg)

    def __str__(self):
        return ("<%s>\n%s" % (self.__class__.__name__,
                              pprint.pformat(list(self.pathlist))))

    def __repr__(self):
        '''
        Return representation of the object
        '''
        return (
            "<%s[%i items]>" % (self.__class__.__name__, len(self._pathdict)))

    @property
    def pathlist(self):
        return set(self._pathdict.keys())

    @pathlist.setter
    def pathlist(self, pathlist):
        """
        Set the pathlist from a list

        :type pathlist: list
        """
        self._pathdict.clear()
        for p in pathlist:
            self.add(p)

    def as_strings(self):
        """
        Return the pathlist as a set of string

        :rtype: list, items:{type:str}
        """
        return [text_to_native_str(str(p)) for p in self.pathlist]

    def add(self, path):
        """
        Append a path to pathlist (only if it exists)

        :param path: path to assert
        :type path: path
        """
        if type(path) in [list, set, tuple]:
            return [self.exists(p) for p in path]
        p = text_to_native_str(str(path))
        if '*' in p:
            # use list_files to create a list of files corresponding to pattern
            # and add the list pathlist
            self.add(list_files(p))
        p = pathlib.Path(path)
        if p not in self.pathlist:
            if p.exists():
                p = p.resolve()
                self._pathdict[p] = 0  # intialize counter
            else:
                self._logger.warning('%s does not exist', p)

    def add_module_path(self, module, *args):
        """
        Append a module path to pathlist

        :param module: module name
        :type module: string
        """
        m = importlib.import_module(module)
        self.add(pathlib.Path(m.__file__).parent.joinpath(args))

    def exists(self, path):
        """
        Check if a path exists in pathlist

        :param path: path or pattern
        :type path: path
        :rtype: bool
        """
        if type(path) in [list, set, tuple]:
            return [self.exists(p) for p in path]
        return bool(self.pick_first(path))

    def pick_first(self, path):
        """
        Pick the first existing match

        :param path: path or pattern
        :type path: str
        :rtype: path
        """
        if type(path) in [list, set, tuple]:
            return [self.pick_first(p) for p in path]
        path = text_to_native_str(str(path))
        path = path.replace('\\', '/')
        recursive = False
        includes = []
        if '**/' in path:
            path, includes = path.split('**/', 1)
            recursive = True
        elif '*' in path:
            bf, af = path.split('*', 1)
            path, inc = bf.rsplit('/', 1)
            includes = '%s*%s' % (inc, af)
            if '**/' in includes:
                recursive = True
                includes = includes.split('**/')[1]
        if os.path.exists(path):
            return pathlib.Path(path)
        optimized_pathlist = sorted(
            list(self._pathdict.items()),
            key=operator.itemgetter(1),
            reverse=True)
        for p, _oldc in optimized_pathlist:
            if p.joinpath(path).exists():
                return next(
                    yield_files(
                        p.joinpath(path), includes, recursive=recursive), None)

    def yield_files(self,
                   includes=["*"],
                   excludes=[],
                   recursive=False,
                   in_parents=False,
                   flatten=True):
        """
        List files in a source directory with a list of given patterns

        :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
        :type includes: [str,list]
        :param excludes: patterns to exclude
        :type excludes: [str,list]
        :param recursive:list files recursively
        :param in_parents: list files recursively in parents
        :param flatten: flatten return lists
        :rtype: array, items:{type: path}
        """
        ret = [None] * len(self._pathdict)
        optimized_pathlist = sorted(
            list(self._pathdict.items()),
            key=operator.itemgetter(1),
            reverse=True)
        for p, _oldc in optimized_pathlist:
            lf = yield_files(p, includes, excludes, recursive, in_parents)
            if flatten:
                for f in lf:
                    yield f
            else:
                yield list(lf)

    def list_files(self,
                   includes=["*"],
                   excludes=[],
                   recursive=False,
                   in_parents=False,
                   flatten=True):
        return list(self.yield_files(includes, excludes, recursive, in_parents, flatten))
