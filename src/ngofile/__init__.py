# -*- coding: utf-8 -*-
__author__ = """Cédric ROMAN"""
__email__ = 'roman@numengo.com'
__version__ = '0.1.0'

import apipkg
apipkg.initpkg(__name__, {
    'advanced_copy': "._copy:advanced_copy",
    'assert_Path': "._assert_path:assert_Path",
    'list_files': "._list_files:list_files",
    'list_files_in_zip': "._list_files:list_files_in_zip",
    'PathList': "._pathlist:PathList",
})
