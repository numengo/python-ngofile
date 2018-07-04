# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 21:20:40 2012

@author: cedric
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from operator import itemgetter

import six
from boto.s3.connection import S3Connection
from dateutil import parser


def get_bucket(aws_access_key_id, aws_secret_access_key, bucket_name):
    connection = S3Connection(aws_access_key_id, aws_secret_access_key)
    return connection.get_bucket(bucket_name, validate=False)

def get_keys_by_dates(bucket):
    old2recent = sorted([(k, parser.parse(k.last_modified)) for k in bucket.list()], key=itemgetter(1))
    return [x[0] for x in old2recent]

def get_latest_key(bucket):
    return get_keys_by_dates(bucket)[-1]
