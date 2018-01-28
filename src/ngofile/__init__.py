# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import apipkg

__author__ = """Cédric ROMAN"""
__email__ = 'roman@numengo.com'
__version__ = '0.1.0'

apipkg.initpkg(
    __name__, {
        'advanced_copy': "._copy:advanced_copy",
        'list_files': "._list_files:list_files",
        'list_files_in_zip': "._list_files:list_files_in_zip",
        'PathList': "._pathlist:PathList",
        'LoadedModules': "._pathlist:LoadModules",
        'list_all_dirs_in_modules': "._pathlist:list_all_dirs_in_modules"
    })
