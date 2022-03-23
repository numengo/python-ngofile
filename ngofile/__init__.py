# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from builtins import str

from past.builtins import basestring

enc = sys.stdout.encoding or "cp850"


def get_unicode(str_or_unicode, encoding=enc):
    if isinstance(str_or_unicode, (str, basestring)):
        return str_or_unicode
    return str(str_or_unicode, encoding, errors='ignore')


__author__ = 'Cédric ROMAN'
__email__ = 'roman@numengo.com'
__version__ = '1.0.1'
