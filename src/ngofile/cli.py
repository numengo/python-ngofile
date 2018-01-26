# -*- coding: utf-8 -*-
"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mngofile` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``ngofile.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``ngofile.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
from __future__ import unicode_literals

import gettext

import click

from ._copy import advanced_copy
from ._list_files import list_files
from ._pathlist import PathList

_ = gettext.gettext


@click.command()
@click.argument('src', nargs=-1)
@click.argument('dst', nargs=-1)
@click.option('--excludes', default=[], help=_('patterns to exclude'))
@click.option('--includes', default=[], help=_('patterns to include'))
@click.option('--recursive', default=True, help=_('copy files recursively'))
@click.option(
    '--create_dirs', default=True, help=_('create missing directories'))
def advanced_copy_cli(src, dst, excludes, includes, recursive, create_dirs):
    advanced_copy(src, dst, excludes, includes, recursive, create_dirs)


@click.command()
@click.argument('src', nargs=-1)
@click.option('--includes', default=["*"], help=_('patterns to include'))
@click.option('--excludes', default=[], help=_('patterns to exclude'))
@click.option('--recursive', default=True, help=_('copy files recursively'))
@click.option(
    '--in_parents',
    default=False,
    help=_('operate recursively in parent folders until root'))
def list_files_cli(srcdir, includes, excludes, recursive, in_parents):
    list_files(srcdir, includes, excludes, recursive, in_parents)
