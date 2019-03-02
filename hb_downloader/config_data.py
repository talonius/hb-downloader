#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2016 Brian Schkerke"
__license__ = "MIT"


class ConfigData(object):
    VERSION = "0.5.0"
    BUG_REPORT_URL = "https://github.com/MayeulC/hb-downloader/issues"
    action = ""
    print_url = False
    download_location = ""
    debug = False
    auth_sess_cookie = ""
    write_md5 = True
    read_md5 = True
    force_md5 = False
    chunk_size = 8192000
    ignore_md5 = False
    resume_downloads = True
    download_product = "-not specified-"

    download_platforms = {
        'audio': True,
        'ebook': True,
        'windows': True,
        'mac': True,
        'linux': True,
        'android': True,
        'asmjs': False
    }
