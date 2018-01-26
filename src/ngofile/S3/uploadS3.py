# -*- coding: utf-8 -*-

#!/usr/bin/python
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import logging
import optparse
import os
import sys
import time

from boto.exception import S3ResponseError
from boto.s3.connection import OrdinaryCallingFormat
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from past.utils import old_div

from . import progressbar
from . import utils

AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = utils.getIdentifiers()

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
        logger.error('progress_callback', exc_info=True)


def upload_file(filename, bucket, prefix=None, reduced_redundancy=False):
    import os.path
    global pbar
    logger = logging.getLogger(__name__)
    # it seems that s3 can only cope with utf-8 (but os.stat only with locale)
    filename_u = filename.encode('utf-8')
    import locale
    c1, c2 = locale.getdefaultlocale()
    filename_l = filename.encode(c2)

    key = Key(bucket)
    if prefix:
        key.key = '%s/%s' % (prefix,
                             os.path.basename(filename_u).replace(' ', '_'))
    else:
        key.key = '%s' % (os.path.basename(filename_u).replace(' ', '_'))

    if key.exists():
        # if key already exists, compute md5 sum to test if necesary to upload
        if os.stat(filename_l)[6] == key.size:
            f = open(filename_l, 'rb')  # rb very important
            md5 = key.compute_md5(f)
            f.close()
            if '"%s"' % md5[0] == key.etag:
                logger.info('file %s is already online' % key.key)
                return key

    size = os.stat(filename_l).st_size
    if size == 0:
        logger.info('Bad filesize for "%s"' % (filename))
        return 0

    widgets = [
        #unicode(filename, errors='ignore').encode('utf-8'), ' ',
        filename_u,
        ' ',
        progressbar.FileTransferSpeed(),
        ' <<<',
        progressbar.Bar(),
        '>>> ',
        progressbar.Percentage(),
        ' ',
        progressbar.ETA()
    ]
    pbar = progressbar.ProgressBar(widgets=widgets, maxval=size)
    pbar.start()

    try:
        key.set_contents_from_filename(
            filename_l,
            cb=progress_callback,
            num_cb=20,
            reduced_redundancy=reduced_redundancy,
        )
        key.set_acl('public-read')
    except IOError as e:
        logger.error('Failed to open file', exc_info=True)
        return 0

    pbar.finish()
    return key


def uploadFileToBucketName(filepath, bucketname, prefix=None):
    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = conn.get_bucket(bucketname)
    upload_file(filepath, bucket, prefix, True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    parser = optparse.OptionParser(usage='usage: %prog [options] ')
    parser.add_option('-p', '--prefix', dest='prefix')
    parser.add_option(
        '-r',
        '--reduced_rendundancy',
        dest='reduced_redundancy',
        action='store_true',
        default=False)
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    conn = S3Connection(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        calling_format=OrdinaryCallingFormat())
    try:
        bucket = conn.get_bucket(args[0])
    except S3ResponseError as e:
        if e.error_code == 'NoSuchBucket':
            bucket = conn.create_bucket(args[0])
        else:
            raise e

    stime = time.time()
    total_bytes = 0
    count = 0
    for arg in args[1:]:
        size = upload_file(arg, bucket, options.prefix,
                           options.reduced_redundancy)
        total_bytes += size
        count += 1

    if len(args) > 2:
        logger.info('%s files %s at %.2f kb/s' %
                    (count, sizeof_fmt(total_bytes),
                     old_div(
                         (old_div(total_bytes, 1024)), time.time()) - stime))
