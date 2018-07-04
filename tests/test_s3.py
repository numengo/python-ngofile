# -*- coding: utf-8 -*-
"""
Unit tests for list_files

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3 
"""
from __future__ import unicode_literals

from os import environ

from ngofile.s3.download import download_file
from ngofile.s3.utils import get_bucket

# change name to avoid automatic test on systems wihout the proper env var
def t_est_s3_download():
    # access key woth restricted read access to a test bucket
    aws_access_key_id = environ['NGO_AWS_ACCESS_KEY_ID']
    aws_secret_access_key = environ['NGO_AWS_SECRET_ACCESS_KEY']
    b = get_bucket(aws_access_key_id, aws_secret_access_key, 'numengo.tests')
    download_file(r'LICENSE', 'LICENSE', b)

if __name__ == '__main__':
    t_est_s3_download()
