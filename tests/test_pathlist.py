# -*- coding: utf-8 -*-
""" Unit tests for ngofile

setup.py - created on 2017/11/15 08:44:32
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3 """
from __future__ import unicode_literals

import logging
from builtins import object
from builtins import str
from pathlib import Path

import ngofile

test_file = Path(__file__).resolve()
test_dir = Path(__file__).resolve().parent


class TestPathList(object):
    logger = logging.getLogger(__name__)

    def test_singleton(self):
        a = ngofile.PathList(test_dir)
        b = ngofile.PathList()
        b.append(str(
            test_dir))  # test_dir is already added during initialisation of a
        assert len(a.pathlist) == 1

    def test_exists(self):
        a = ngofile.PathList(test_dir)
        p2 = a.pick_first(test_file.name)
        assert p2.exists()
        assert not a.exists('dummy.dum')


if __name__ == '__main__':
    pass
    # TestPathList.test_singleton()
    # TestPathList.test_exists()
