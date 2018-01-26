# coding: utf-8
"""
2017/11/12: C.ROMAN (in africa)
functions/class to deal with filepathes
"""
from __future__ import unicode_literals
import logging
from builtins import object
from builtins import str
from pathlib import Path

from ._list_files import list_files
from ._assert_path import assert_Path
try:
    unicode = str
except Exception:
    pass

class PathList(object):
    """ path list manager """
    _instance = None
    _pathlist = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance and kwargs.get('singleton',True):
            cls._instance = super(PathList, cls).__new__(cls)
            return cls._instance
        else:
            cls._pathlist = []
            return super(PathList, cls).__new__(cls)

    def __init__(self,*args,**kwargs):
        """ appends each arg as a path of pathlist
        if `pathlist` is given as keyword argument used as pathlist."""
        self.logger = logging.getLogger(__name__)
        for arg in args:
            if arg:
                self.append(arg)
        if 'pathlist' in list(kwargs.keys()):
            self.set_pathlist(kwargs.get('pathlist'))

    def __repr__(self):
        '''Returns representation of the object'''
        return("{}[{}]('{}')".format(self.__class__.__name__,len(self._pathlist), self._pathlist))

    @property
    def pathlist(self):
        return self._pathlist

    @pathlist.setter
    def set_pathlist(self, pathlist):
        """ set the pathlist from a list
        :param pathlist: path list to set
        :rtype pathlist: list"""
        for p in pathlist:
            self.append(p)

    def as_strings(self):
        """ returns the pathlist as a list of string
        :rtype: list"""
        return [str(p) for p in self._pathlist]

    def append(self, path):
        """ append a path to pathlist (only if it exists)

        :param path: path to assert
        :type path: str/pathlib.Path"""
        if isinstance(path,list):
            return [self.append(p) for p in path]
        p = assert_Path(path)
        if str(p) not in self.as_strings():
            if p.exists():
                self._pathlist.append(p.resolve())
            else:
                 self.logger.warning('%s does not exist' % p)
        else:
             self.logger.warning('%s already in pathlist' % p)

    def exists(self, path):
        """ check if a path exists in pathlist

        :param path: path or pattern
        :type path: str/pathlib.Path
        :rtype: boolean"""
        if isinstance(path,list):
            return [self.exists(p) for p in path]
        return len(self.list_files(path)) > 0

    def pick_first(self, path):
        """ picks the first existing match

        :param path: path or pattern
        :type path: str/pathlib.Path
        :rtype: pathlib.Path/None """
        if isinstance(path,list):
            return [self.exists(p) for p in path]
        ms = self.list_files(path)
        if len(ms) > 0:
            return ms[0]

    def list_files(self,includes=["*"], excludes=[], recursive=False, in_parents=False):
        """ list files in a source directory with a list of given patterns 
        
        :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
        :type includes: str/list
        :param excludes: patterns to exclude
        :type excludes: str/list
        :param recursive:list files recursively
        :param in_parents: list files recursively in parents
        :rtype: ngomodel.TypedList(pathlib.Path)
        """
        ret = []
        for p in self._pathlist:
            ret += list_files(p,includes,excludes,recursive,in_parents)
        return ret
