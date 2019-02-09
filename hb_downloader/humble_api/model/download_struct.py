#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .base_model import BaseModel
from urllib.parse import urlparse

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class DownloadStruct(BaseModel):
    """
        This contains the actual download information for a given download.

        sha1:  The SHA1 checksum for the item.
        md5:  The MD5 checksum for the item.
        name:  The name of the item.  Sometimes very useless.
        url:  The URLs to use for downloading the item, either via BitTorrent or the web.
        human_size:  A human readable size for the item.
        file_size:  A machine readable size for the item.  This is used during MD5 calculations.
        small:  0 or 1.  Unknown purpose.
    """

    def __init__(self, data):
        """
            Parameterized constructor for the DownloadStruct object.

            :param data: The JSON data to define the object with.
        """
        super(DownloadStruct, self).__init__(data)

        self.sha1 = data.get("sha1", None)
        self.name = data.get("name", None)
        self.human_size = data.get("human_size", None)
        self.file_size = data.get("file_size", None)
        self.md5 = data.get("md5", None)
        self.small = data.get("small", None)
        self.uses_kindle_sender = data.get("uses_kindle_sender", None)
        self.kindle_friendly = data.get("kindle_friendly", None)
        self.download_web = None
        self.download_bittorrent = None

        url_dictionary = data.get("url", None)
        if url_dictionary is not None:
            self.download_web = url_dictionary.get("web", None)
            self.download_bittorrent = url_dictionary.get("bittorrent", None)
        self.filename = self.__determine_filename()

    def __determine_filename(self):
        """
            Determines the filename for the current download using the URL as it's basis.

            :return:  The filename to use when saving this download to the local filesystem.
            :rtype: str
        """
        work_value = ""

        if self.download_web is None and self.download_bittorrent is None:
            work_value = ""
        elif self.download_web is not None:
            work_value = self.download_web
        elif self.download_bittorrent is not None:
            work_value = self.download_bittorrent

        parsed_url = urlparse(work_value)
        filename = parsed_url[2]  # https://docs.python.org/2/library/urlparse.html

        if filename.startswith("/"):
            filename = filename[1:]
        filename = filename.replace("/", "_")

        return filename
