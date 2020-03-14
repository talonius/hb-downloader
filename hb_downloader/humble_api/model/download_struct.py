#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .base_model import BaseModel
from urllib.parse import urlparse
from email.utils import parsedate
from datetime import datetime
import requests

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
        timestamp: a date & time. Used for displaying 'Updated' info on web page
        last_modified: value taken from file URL, useful for files that have no timestamp
    """

    def __init__(self, data, get_extra_file_info=False):
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

        # if a download url is available get the file timestamp from the server, this cannot
        #  be used when the API timestamp (see below) is not set.
        # NOTE: this *drastically* increases time required to get all data, so is only done if
        #       specficially requested
        # NOTE: in some cases last_modified is different to timestamp by a day or so (probably
        #       due to uploading later than expected)
        if get_extra_file_info and (self.download_web is not None):
            file_info_response = requests.Session().request("HEAD", self.download_web)
            if file_info_response.status_code == requests.codes.ok:
                self.last_modified = file_info_response.headers.get('Last-Modified', None)

        if self.last_modified is not None:
            # convert date to ISO 8601 format, ignore time portion
            # NOTE: this could be made simpler by not use email.utils and parsing it directly, using
            #       email.utils allows for parsing values more robustly and will catch edge cases
            #       that direct parsing may not
            self.last_modified = datetime(*parsedate(self.last_modified)[:6]).strftime('%Y-%m-%d')
        else:
            # to make other code simpler store the 'epoch' date for
            # anything that doesn't have a date
            self.last_modified = '1970-01-01'

        # timestamp is relatively new addition to the API, not all files have it set
        self.timestamp = data.get("timestamp", None)
        if self.timestamp is not None:
            # convert date to ISO 8601 format, ignore time portion
            self.timestamp = datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d')
        else:
            # to make other code simpler store the 'epoch' date for
            # anything that doesn't have a date
            self.timestamp = '1970-01-01'

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
