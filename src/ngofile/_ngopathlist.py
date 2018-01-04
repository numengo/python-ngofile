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

from ._ngofilelist import list_files
from ._assert_path import assert_Path
try:
    unicode = str
except Exception:
    pass

class NgoPathList(object):
    """ path list manager """
    _instance = None
    _pathlist = []

    def __new__(cls, *args, **kwargs):
        if not cls._instance and kwargs.get('singleton',True):
            cls._instance = super(NgoPathList, cls).__new__(cls)
            return cls._instance
        else:
            return super(NgoPathList, cls).__new__(cls)

    def __init__(self,*args,**kwargs):
        """ appends each arg as a path of pathlist
        if `pathlist` is given as keyword argument used as pathlist."""
        self.logger = logging.getLogger(__name__)
        for arg in args:
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
        :rtype pathlist: list of string or pathlib.Path"""
        for p in pathlist:
            self.append(p)

    def as_strings(self):
        """ returns the pathlist as a list of string
        :rtype: list of strings"""
        return [str(p) for p in self._pathlist]

    def append(self, path):
        """ append a path to pathlist

        :param path: path to assert
        :type path: string or pathlib.Path"""
        if isinstance(path,list):
            return [self.append(p) for p in path]
        p = assert_Path(path).resolve()
        if str(p) not in self.as_strings():
            self._pathlist.append(p.resolve())
        else:
             self.logger.warning('%s already in pathlist' % p)

    def exists(self, path):
        """ check if a path exists in pathlist

        :param path: path or pattern
        :type path: string or pathlib.Path
        :rtype: boolean"""
        if isinstance(path,list):
            return [self.exists(p) for p in path]
        return len(self.list_files(path)) > 0

    def pick_first(self, path):
        """ picks the first existing match

        :param path: path or pattern
        :type path: string or pathlib.Path
        :rtype: pathlib.Path or None """
        if isinstance(path,list):
            return [self.exists(p) for p in path]
        ms = self.list_files(path)
        if len(ms) > 0:
            return ms[0]

    #def all_matches(self, path):
    #    """ returns all matches in pathlist
    #
    #    :param path: path or pattern
    #    :type path: string or pathlib.Path
    #    :rtype: list of pathlib.Path """
    #    if isinstance(path,list):
    #        return [self.exists(p) for p in path]
    #    matches = [p.glob(str(path)) for p in self._pathlist]
    #    return [item for sublist in matches for item in sublist]
    #    
    def list_files(self,includes=["*"], excludes=[], recursive=False, in_parents=False):
        """ list files in a source directory with a list of given patterns 
        
        :param includes: pattern or list of patterns ('*.py', '*.txt', etc...)
        :type includes: string or list of strings
        :param excludes: patterns to exclude
        :type excludes: string or list of strings
        :param recursive:list files recursively
        :type recursive: boolean
        :param in_parents: list files recursively in parents
        :type in_parents: boolean
        :rtype: list of pathlib.Path
        """
        ret = []
        for p in self._pathlist:
            ret += list_files(p,includes,excludes,recursive,in_parents)
        return ret
