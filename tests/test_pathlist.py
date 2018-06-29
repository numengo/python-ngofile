# -*- coding: utf-8 -*-
"""
Unit tests for ngofile

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3 
"""
from __future__ import unicode_literals

import logging
from builtins import object
from builtins import str
from pathlib import Path

from ngofile.pathlist import PathList

test_file = Path(__file__).resolve()
test_dir = Path(__file__).resolve().parent


class TestPathList(object):
    logger = logging.getLogger(__name__)

    def test_singleton(self):
        a = PathList(test_dir)
        b = PathList()
        b.add(str(
            test_dir))  # test_dir is already added during initialisation of a
        assert len(a.pathlist) == 1

    def test_exists(self):
        a = PathList(test_dir)
        p2 = a.pick_first(test_file.name)
        assert p2.exists()
        assert not a.exists('dummy.dum')


if __name__ == '__main__':
    TestPathList().test_singleton()
    TestPathList().test_exists()
