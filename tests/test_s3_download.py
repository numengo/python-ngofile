# -*- coding: utf-8 -*-
"""
Unit tests for list_files

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3 
"""
from __future__ import unicode_literals

from ngofile.s3.download import download_file
from ngofile.s3.utils import get_bucket

def test_s3_download():
    # access key woth restricted read access to a test bucket
    AWS_ACCESS_KEY_ID='AKIAJ6UBDYZFCP47PQGQ'
    AWS_SECRET_ACCESS_KEY='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'
    b = get_bucket(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, 'numengo.tests')
    download_file(r'LICENSE', 'LICENSE', b)

if __name__ == '__main__':
    test_s3_download()
