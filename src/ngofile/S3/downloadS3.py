# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
from builtins import str

#!/usr/bin/python
from . import progressbar
from . import utils

#AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = utils.getIdentifiers()

pbar = None


def sizeof_fmt(num):
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0


def progress_callback(current, total):
    try:
        pbar.update(current)
    except AssertionError as e:
        logger = logging.getLogger(__name__)
        logger.error('progress_callback failed : ', exc_info=True)


def download_file(filename, key, bucket, prefix=None,
                  reduced_redundancy=False):
    global pbar
    if prefix:
        key = bucket.get_key('%s/%s' (prefix, key))
    else:
        key = bucket.get_key(key)

    if os.path.exists(filename):
        if os.stat(filename)[6] == key.size:
            f = open(filename, 'rb')  # rb very important
            md5 = key.compute_md5(f)
            f.close()
            if '"%s"' % md5[0] == key.etag:
                logger = logging.getLogger(__name__)
                logger.info('file %s is already uptodate' % str(key.key, enc))
                return key

    size = key.size
    """
    widgets = [
        unicode(filename, errors='ignore').encode('utf-8'), ' ',
        progressbar.FileTransferSpeed(),
        ' <<<', progressbar.Bar(), '>>> ',
        progressbar.Percentage(), ' ', progressbar.ETA()
    ]
    """
    widgets = [
        filename, ' ',
        progressbar.FileTransferSpeed(), ' <<<',
        progressbar.Bar(), '>>> ',
        progressbar.Percentage(), ' ',
        progressbar.ETA()
    ]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=size)
    pbar.start()

    try:
        key.get_contents_to_filename(filename, cb=progress_callback, num_cb=20)
    except IOError as e:
        logger = logging.getLogger(__name__)
        logger.error('download_file failed : ', exc_info=True)
        return 0

    pbar.finish()
    return key


def test():
    c = utils.getS3Connection()
    b = c.get_bucket('numengo.builds')
    download_file(r'K:\distrib\essai2.zip', 'essai.zip', b)
