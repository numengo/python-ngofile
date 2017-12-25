# -*- coding: utf-8 -*-
""" Unit tests for ngofilelist

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

class TestNgoFileList(TestCase):

    def test_list_files_with_patterns(self):
        fs = list_files_with_patterns(test_dir)
        assert len(fs)>=1
        fs = list_files_with_patterns(test_dir,'test_*.py')
        assert len(fs)>=1
        fs = list_files_with_patterns(test_dir,['test_*.py'])
        assert len(fs)>=1

    def test_list_files(self):
        fs = list_files(test_dir)
        assert len(fs)>=1
        try:
            fs = list_files(test_file)
            assert False,"should have thrown an exception"
        except:
            pass
        fs2 = list_files(test_dir,["*.py"])
        assert len(fs)-len(fs2)>0
        fs3 = list_files_with_patterns(test_dir,'*.py',recursive=False)
        assert len(fs)-len(fs2)==len(fs3)

    def test_list_files_to_move(self):
        dest = Path('new_dir') # doesn't need to exist so far
        fs = list_files_to_move(test_dir,dest,['*.pyc'])
        for f in fs:
            self.logger.info(f)

    def list_files_in_zip(self):
        f = test_dir.joinpath('tmp_dir_py.zip')
        z = zipfile.ZipFile(str(f.resolve()),'r')
        ls1 = list_files_in_zip(z, "**/*.py", excludes=[], recursive=False)
        ls2 = list_files_in_zip(z, "*.py", excludes=[], recursive=True)
        ls3 = list_files_in_zip(z, "*", excludes=["*.txt"], recursive=True)
        assert len(ls1)==len(ls2)
        assert len(ls2)==len(ls3)
        z.close()

if __name__ == '__main__':
    pytest.main()