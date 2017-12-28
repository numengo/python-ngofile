# coding: utf-8
"""
2017/11/12: C.ROMAN (in africa)
functions/class to deal with filepathes
"""
from __future__ import unicode_literals
import logging
import os
import os.path
import sys
from builtins import object
from builtins import str
from pathlib import Path

import ngofile


class NgoPathList(object):
    """ path list manager
    
    if given arguments at initialization, append each arg as a path
    """
    _instance = None
    _pathlist = []

    def __new__(cls, *args, **kwargs):
        logger = logging.getLogger(__name__)
        if not cls._instance:
            cls._instance = super(NgoPathList, cls).__new__(cls)
        if 'pathlist' in list(kwargs.keys()):
            cls._instance.set_pathlist(pathlist)
        for arg in args:
            cls._instance.append(arg)
        return cls._instance

    @property
    def pathlist(self):
        return self._pathlist

    @pathlist.setter
    def set_pathlist(self, pathlist):
        for p in pathlist:
            self._pathlist.append(p)

    def __repr__(self):
        return '<NgoPathList>', self._pathlist

    def as_strings(self):
        """ returns the pathlist as a list of string"""
        return [str(p.resolve()) for p in self._pathlist]

    def append(self, path):
        """ append a path to pathlist """
        logger = logging.getLogger(__name__)
        p = Path(path)
        if p.exists():
            if str(p.resolve()) not in self.as_strings():
                self._pathlist.append(p.resolve())
            else:
                logger.warning('%s already in pathlist' % p)
        else:
            logger.warning(
                '%s not added to pathlist because it does not exist' % p)

    def exists(self, path):
        """ check if a path exists in pathlist """
        return len(self.all_matches(path)) > 0

    def pick_first(self, path):
        """ picks the first existing match"""
        ms = self.all_matches(path)
        if len(ms) > 0:
            return ms[0]

    def all_matches(self, path):
        """ returns all matches """
        p = Path(path)
        return [
            p2.joinpath(p) for p2 in self._pathlist if p2.joinpath(p).exists()
        ]
