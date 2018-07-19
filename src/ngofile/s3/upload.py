# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import optparse
import os
import ssl
import sys
import time
from pathlib import Path
import locale
import glob
import multiprocessing
import subprocess
import contextlib
import functools

from boto.exception import S3ResponseError
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from boto.s3.multipart import MultiPartUpload
from multiprocessing.pool import IMapIterator

from . import progress_bar
from . import utils

if hasattr(ssl, '_create_unverified_context'):
   ssl._create_default_https_context = ssl._create_unverified_context

pbar = None

def sizeof_fmt(num):
    for x in ['bytes','KB','MB','GB','TB']:
        if num < 1024.0:
            return "%3.1f%s" % (num, x)
        num /= 1024.0

def progress_callback(current, total):
    try:
        pbar.update(current)
    except AssertionError as e:
        logger = logging.getLogger(__name__)
        logger.error('progress_callback', exc_info=True)		

def upload_file(filepath, bucket, prefix=None, reduced_redundancy=False):
    global pbar
    logger = logging.getLogger(__name__)
    if not isinstance(filepath, Path):
        filepath = Path(filepath)
    # it seems that s3 can only cope with utf-8 (but os.stat only with locale)
    c1, c2 = locale.getdefaultlocale()
    #filename_u = str(filepath.name).encode('utf-8')
    #filename_l = str(filepath.name).encode(c2)
    
    key = Key(bucket)
    if prefix:
        key.key = '%s/%s' % (prefix, filepath.name.replace(' ','_'))
    else:
        key.key = '%s' % (filepath.name.replace(' ','_'))

    if key.exists():
        # if key already exists, compute md5 sum to test if necesary to upload
        if filepath.stat().st_size == key.size:
            f = filepath.open('rb') # rb very important
            md5 = key.compute_md5(f)
            f.close()
            if '"%s"'%md5[0] == key.etag:
                logger.info('file %s is already online'%key.key)
                return key

    size = filepath.stat().st_size
    if size == 0:
        logger.info('Bad filesize for "%s"', filepath)
        return 0

    widgets = [
        #unicode(filename, errors='ignore').encode('utf-8'), ' ',
        #filepath.name.encode('utf-8'), ' ',
        str(filepath), ' ',
        progress_bar.FileTransferSpeed(),
        ' <<<', progress_bar.Bar(), '>>> ',
        progress_bar.Percentage(), ' ', progress_bar.ETA()
    ]
    pbar = progress_bar.ProgressBar(widgets=widgets, maxval=size)
    pbar.start()

    try:
        key.set_contents_from_filename(
            #str(filepath).encode(c2),
            str(filepath),
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

def upload_file_to_bucketname(connection, filepath, bucketname, prefix=None):
    #connection = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    bucket = connection.get_bucket(bucketname, validate=False)
    upload_file(filepath, bucket, prefix, True)


def mp_from_ids(mp_id, filepath, bucket):
    """Get the multipart upload from the bucket and multipart IDs.
    This allows us to reconstitute a connection to the upload
    from within multiprocessing functions.
    """
    #conn = boto.connect_s3()
    #bucket = conn.lookup(mp_bucketname)
    #bucket = connection.get_bucket(bucketname, validate=False)
    mp = MultiPartUpload(bucket)
    mp.key_name = filepath
    mp.id = mp_id
    return mp

def map_wrap(f):
    @functools.wraps(f)
    def wrapper(args, **kwargs):
        return f(*args, **kwargs)
    return wrapper

@map_wrap
def transfer_part(mp_id, filepath, bucket, i, part):
    """Transfer a part of a multipart upload. Designed to be run in parallel.
    """
    mp = mp_from_ids(mp_id, filepath, bucket)
    print(" Transferring", i, part)
    encoding = 'utf-8'
    encoding = 'cp850'
    import codecs
    with codecs.open(part, 'r', encoding) as t_handle:
        mp.upload_part_from_file(t_handle, i+1)
    os.remove(part)

@contextlib.contextmanager
def multimap(cores=None):
    """Provide multiprocessing imap like function.
    The context manager handles setting up the pool, worked around interrupt issues
    and terminating the pool on completion.
    """
    if cores is None:
        cores = max(multiprocessing.cpu_count() - 1, 1)
    def wrapper(func):
        def wrap(self, timeout=None):
            return func(self, timeout=timeout if timeout is not None else 1e100)
        return wrap
    IMapIterator.next = wrapper(IMapIterator.next)
    pool = multiprocessing.Pool(cores)
    yield pool.imap
    pool.terminate()

def _multipart_upload(bucket, s3_key_name, tarball, mb_size, use_rr=True):
    """Upload large files using Amazon's multipart upload functionality.
    """
    cores = multiprocessing.cpu_count()
    def split_file(in_file, mb_size, split_num=5):
        prefix = os.path.join(os.path.dirname(in_file),
                              "%sS3PART" % (os.path.basename(s3_key_name)))
        split_size = int(min(mb_size / (split_num * 2.0), 250))
        if not os.path.exists("%saa" % prefix):
            cl = ["split", "-b%sm" % split_size, in_file, prefix]
            subprocess.check_call(cl)
        return sorted(glob.glob("%s*" % prefix))

    mp = bucket.initiate_multipart_upload(s3_key_name, reduced_redundancy=use_rr)
    with multimap(cores) as pmap:
        for _ in pmap(transfer_part, ((mp.id, mp.key_name, bucket, i, part)
                                      for (i, part) in
                                      enumerate(split_file(tarball, mb_size, cores)))):
            pass
    mp.complete_upload()

def multipart_upload_file(filepath, bucket, prefix=None):
    filepath.resolve()
    mb_size = filepath.stat().st_size / 1e6
    s3_key_name = filepath.name
    if prefix:
        s3_key_name = '%s/%s' % (prefix, filepath.name.replace(' ','_'))
    else:
        s3_key_name = '%s' % (filepath.name.replace(' ','_'))
    _multipart_upload(bucket, s3_key_name, str(filepath), mb_size)

def multipartupload_file_to_bucketname(connection, filepath, bucketname, prefix=None):
    bucket = connection.get_bucket(bucketname, validate=False)
    multipart_upload_file(filepath, bucket, prefix=None)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)    
    logger = logging.getLogger(__name__)

    parser = optparse.OptionParser(usage='usage: %prog [options] ')
    parser.add_option('-p', '--prefix', dest='prefix')
    parser.add_option('-r', '--reduced_rendundancy', dest='reduced_redundancy', action='store_true', default=False)
    (options, args) = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        sys.exit(1)

    conn = S3Connection(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
    try:
        bucket = conn.get_bucket(args[0])
    except S3ResponseError as e:
        if e.error_code == 'NoSuchBucket':
            bucket = conn.create_bucket(args[0], validate=False)
        else:
            raise e

    stime = time.time()
    total_bytes = 0
    count = 0
    for arg in args[1:]:
        size = upload_file(arg, bucket, options.prefix, options.reduced_redundancy)
        total_bytes += size
        count += 1

    if len(args) > 2:
        logger.info('%s files %s at %.2f kb/s', count, sizeof_fmt(total_bytes), 
                    (total_bytes / 1024)/time.time() - stime)
