# -*- coding: utf-8 -*-
"""
Entrypoint module, in case you use `python -mngofile`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""
from __future__ import unicode_literals

from ngofile.cli import list_files_cli

if __name__ == "__main__":
    list_files_cli()
