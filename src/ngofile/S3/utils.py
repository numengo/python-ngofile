# -*- coding: utf-8 -*-
"""
Created on Sun Feb 05 21:20:40 2012

@author: cedric
"""
from __future__ import unicode_literals

import os
import os.path

from boto.s3.connection import OrdinaryCallingFormat


def getIdentifiers():
    """ parse private files with id and access key and return it"""
    try:
        access = os.path.join(os.path.dirname(__file__), 'access.id')
        f = open(access)
        access = f.read()
        f.close()
        AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = access.split()
        return AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
    except:
        raise Exception(
            'Impossible to find access identifiers for S3 in %s file' % access)


def getS3Connection():
    from boto.s3.connection import S3Connection
    AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY = getIdentifiers()
    return S3Connection(
        AWS_ACCESS_KEY_ID,
        AWS_SECRET_ACCESS_KEY,
        calling_format=OrdinaryCallingFormat())


def getKeysSortedByDates(bucket):
    from dateutil import parser
    from operator import itemgetter
    old2recent = sorted(
        [(k, parser.parse(k.last_modified)) for k in bucket.list()],
        key=itemgetter(1))
    return [x[0] for x in old2recent]


def getLatestKey(bucket):
    return getKeysSortedByDates(bucket)[-1]
