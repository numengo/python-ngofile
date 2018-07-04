# *- coding: utf-8 -*-
"""click API for NgoFile"""
import gettext

import click

from ngofile.copy import advanced_copy
from ngofile.list_files import list_files

_ = gettext.gettext


@click.command()
@click.argument('names', nargs=-1)
def main(names):
    click.echo(repr(names))


########################
# FUNCTIONS ENTRY POINTS
########################


@click.command()
@click.argument('src')
@click.option(
    '--includes',
    default=[u'*'],
    help=_('pattern or list of patterns (*.py, *.txt, etc...)'))
@click.option('--excludes', help=_('pattern or patterns to exclude'))
@click.option('--recursive', help=_('list files recursively'))
@click.option('--in_parents', help=_('list files recursively in parents'))
@click.option(
    '--folders',
    default=0,
    help=_('0: without folders, 1: with folders, 2: only folders'))
def list_files_cli(ctx, src, includes, excludes, recursive, in_parents,
                   folders):
    """ list files in a source path with a list of given patterns 
    if src contains patterns, modifies initial source dir and create corresponding includes patterns"""
    list_files()


@click.command()
@click.argument('src')
@click.argument('dst')
@click.option('--excludes', help=_('list of patterns to exclude'))
@click.option('--includes', help=_('list of patterns to include'))
@click.option('--recursive', default=True, help=_('recursive copy'))
@click.option(
    '--create_directory', default=True, help=_('create missing directories'))
def advanced_copy_cli(ctx, src, dst, excludes, includes, recursive,
                      create_directory):
    """ copy a directory structure src to destination """
    advanced_copy()
