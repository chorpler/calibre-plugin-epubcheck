#!/usr/bin/env python2
# vim:fileencoding=utf-8
from __future__ import (unicode_literals, division, absolute_import,
                        print_function)

__license__ = 'GPL v3'
__copyright__ = '2018, 2019, 2020, 2021, 2022, 2023 Doitsu'

from calibre.customize import EditBookToolPlugin

class DemoPlugin(EditBookToolPlugin):

    name = 'EpubCheck'
    version = (0, 3, 0)
    author = 'Doitsu'
    supported_platforms = ['windows', 'osx', 'linux']
    description = 'A simple EpubCheck 5.1.0 wrapper.'
    minimum_calibre_version = (5, 13, 0)
