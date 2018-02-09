# -*- coding: utf-8 -*-
""" Unit tests for _list_files

setup.py - created on 2017/11/15 08:44:32
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3 """
from __future__ import unicode_literals

import zipfile
from builtins import object
from builtins import str
from pathlib import Path

import pytest

import ngofile
import ngofile.exceptions

test_file = Path(__file__).resolve()
test_dir = Path(__file__).resolve().parent
test_dir_a = test_dir.joinpath('a')


def test_list_files_with_patterns():
    # works with Path object
    fs1 = ngofile.list_files(test_dir_a, recursive=True)
    # works with path as a string
    fs2 = ngofile.list_files(str(test_dir_a), recursive=True)
    assert len(fs1) == len(fs2)
    # only selects *.py files
    fs = ngofile.list_files(test_dir_a, "*.data", recursive=True)
    assert len(fs) == 9
    # only selects *.py and *.txt files
    fs = ngofile.list_files(test_dir_a, ["*.data", "*.txt"], recursive=True)
    assert len(fs) == 18
    # only selects *.py files, but excludes b and bb directories
    fs = ngofile.list_files(
        test_dir_a, "*.data", ["bb", "bbb"], recursive=True)
    assert len(fs) == 4

    with pytest.raises(ngofile.exceptions.NotADirectoryException):
        fs = ngofile.list_files(test_file)


def test_list_files_in_zip():
    f = test_dir.joinpath('tmp_dir_py.zip')
    z = zipfile.ZipFile(str(f), 'r')
    ls1 = ngofile.list_files_in_zip(z, "*.py", excludes=[], recursive=True)
    ls2 = ngofile.list_files_in_zip(z, "*", excludes=["*.txt"], recursive=True)
    assert len(ls2) >= len(ls1)  # because ls1 contains folders too
    z.close()


def test_list_files_with_included_dir():
    src = r'D:\code\python-ngofile'
    excludes = ['docs', '.*', 'dist', 'build']
    includes = ['*.json', '*.yaml', '*.rst', '*.mtm', 'templates/*']
    from pprint import pprint
    ls = ngofile.list_files(src, includes, excludes)
    pprint(ls)


if __name__ == '__main__':
    test_list_files2()
