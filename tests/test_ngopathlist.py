# -*- coding: utf-8 -*-
""" Unit tests for ngofile

setup.py - created on 2017/11/15 08:44:32
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3 """
import os
import os.path
import sys

import pytest

import logging
logging.basicConfig(level=logging.DEBUG)
from ngoutils import *

from pathlib import Path
test_file = Path(__file__).resolve()
test_dir = Path(__file__).resolve().parent

from ngofile import *
        
class TestNgoPathList(TestCase):

    def test_singleton(self):
        a = NgoPathList(test_dir)
        b = NgoPathList()
        b.append(str(test_dir)) # test_dir is already added during initialisation of a
        assert len(a.pathlist)==1

    def test_exists(self):
        a = NgoPathList(test_dir)
        p2 = a.pick_first(test_file.name)
        assert p2.exists()
        assert not a.exists('dummy.dum')

if __name__ == '__main__':
    pytest.main()
