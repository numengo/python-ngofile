========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/python-ngofile/badge/?style=flat
    :target: https://readthedocs.org/projects/python-ngofile
    :alt: Documentation Status

.. |travis| image:: https://travis-ci.org/numengo/python-ngofile.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/numengo/python-ngofile

.. |codecov| image:: https://codecov.io/github/numengo/python-ngofile/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/numengo/python-ngofile

.. |version| image:: https://img.shields.io/pypi/v/ngofile.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/ngofile

.. |commits-since| image:: https://img.shields.io/github/commits-since/numengo/python-ngofile/v1.0.1.svg
    :alt: Commits since latest release
    :target: https://github.com/numengo/python-ngofile/compare/v1.0.1...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/ngofile.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/ngofile

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/ngofile.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/ngofile

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/ngofile.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/ngofile


.. end-badges

misc file utilities

* Free software: GNU General Public License v3

.. skip-next

Installation
============

Install command::

    pip install ngofile

Documentation
=============

https://python-ngofile.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
