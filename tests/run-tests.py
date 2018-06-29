#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" 
start-up script to launch all units tests 
"""
from __future__ import unicode_literals

import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import pytest
    pytest.main()
