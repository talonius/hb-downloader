#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
from hb_downloader.config_data import ConfigData
from hb_downloader.humble_api.events import Events
from hb_downloader.humble_api.humble_hash import HumbleHash
from hb_downloader import logger

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2020 Brian Schkerke"
__license__ = "MIT"

def format_filesize(filesize):
    prefixes = [' bytes', ' KiB', ' MiB', ' GiB', ' TiB']
    index_level = 0

    if not filesize:
        return None

    while abs(filesize / 1024) > 1 and index_level < len(prefixes) - 1:
        index_level += 1
        filesize /= 1024

    try:
        size = "%.2f%s" % (filesize, prefixes[index_level])
    except:
        size = "unknown"
        pass
    return size

class HumbleDownload(object):
    order_number = ""
    humble_md5 = ""
    filename = ""
    platform = ""
    product_name = ""
    product_name_machine = ""
    subproduct_name = ""
    download_url = ""
    humble_file_size = 0
    humble_file_size_human = ""
    machine_name = ""
    status_message = ""
    requires_download = False
    partial_download = False

    def __init__(self, cd, cds, co, csp, cv):
        self.order_number = cv
        self.download_url = cds.download_web
        self.filename = cds.filename
        self.humble_file_size = cds.file_size
        self.humble_file_size_human = format_filesize(cds.file_size) or cds.human_size
        self.platform = cd.platform
        self.product_name = co.product.human_name
        self.product_name_machine = co.product.machine_name
        self.subproduct_name = csp.product_name
        self.humble_md5 = cds.md5
        self.machine_name = cd.machine_name

    @property
    def local_file_size(self):
        """
            Returns the size of the file.

            :return:  A value representing the size of the file.
        """
        if os.path.exists(self.full_filename):
            return os.path.getsize(self.full_filename)
        else:
            return 0

    @property
    def md5_matches(self):
        """
            Determines whether the local MD5 matches the Humble Bundle
            specified MD5.

            :return:   True or False depending upon whether the MD5 checksums
            match.
            :rtype:  bool
        """
        if len(self.local_md5) == 0:
            return False
        else:
            return self.humble_md5 == self.local_md5

    @property
    def local_md5(self):
        """
            Returns the MD5 of the local file.

            :return:  The checksum for the local file.
        """
        if os.path.exists(self.full_filename):
            return HumbleHash.checksum(self.full_filename)
        else:
            return ""

    @property
    def full_filename(self):
        """
            Calculates and returns the full path and filename for the current
            Humble Bundle download.

            :return:  The full path and filename for the current download.
        """

        # TODO HK: add options for path structure from commandline and or cfg file

        if not ConfigData.folderstructure_OrderName:
            temp_full_filename = os.path.join(
                ConfigData.download_location,
				self.subproduct_name, self.platform,
				self.filename)
        else:
            temp_full_filename = os.path.join(
                ConfigData.download_location,
                self.product_name_machine, self.subproduct_name, self.platform,
                self.filename)

        return temp_full_filename

    def remove(self):
        """
            Removes the file associated with the Humble Bundle download and any
            accompanying MD5 file.

            :return:  None
        """
        if os.path.exists(self.full_filename):
            os.remove(self.full_filename)
            HumbleHash.remove_md5file(self.full_filename)

    def check_status(self):
        """
            This method determines whether or not the given file has already
            been successfully downloaded.

            :return:  True if the existing file matches size and checksum
            verification.
        """
        if not os.path.exists(self.full_filename):
            self.status_message = "Target %s doesn't exist." % self.filename
            self.requires_download = True
        elif not self.humble_file_size == self.local_file_size:
            self.status_message = (
                    "%s file sizes don't match (expected %d actual %d)." %
                    (self.filename,
                     self.humble_file_size or 0,
                     self.local_file_size or 0))
            self.partial_download = True
            self.requires_download = True
        elif not ConfigData.ignore_md5:
            if not self.md5_matches:
                self.status_message = (
                        "MD5 of %s doesn't match (expected %s actual %s)." %
                        (self.filename,
                         self.humble_md5,
                         self.local_md5))
                self.requires_download = True
        else:
            self.requires_download = False

        return not self.requires_download

    def download_file(self):
        """ Downloads a file from the location specified in the provided
            DownloadStruct.
        """
        self.__create_directory()

        if not ConfigData.resume_downloads:
            self.remove()

        Events.trigger(Events.EVENT_DOWNLOAD_START, self.filename)

        if ConfigData.resume_downloads and self.local_file_size > 0:
            self.__resume_download()
        else:
            self.__start_download()

        Events.trigger(Events.EVENT_DOWNLOAD_END, self.filename)

    def __resume_download(self):
        """ Resumes a download if the server supports it. """
        resume_header = {'Range': 'bytes=%d-' % self.local_file_size}
        web_request = requests.get(
                self.download_url, headers=resume_header, stream=True)
        mode = "ab"
        self.__download_file(web_request, mode, self.local_file_size)

    def __start_download(self):
        """ Starts a download afresh. """
        web_request = requests.get(self.download_url, stream=True)
        mode = "wb"
        self.__download_file(web_request, mode, 0)

    def __download_file(self, web_request, mode, read_bytes=0):
        current_percentage = 0

        with open(self.full_filename, mode) as f:
            # For a download that's resumed the content-length will be the
            # remaining bytes, not the total.
            # total_length = int(web_request.headers.get("content-length"))
            total_length = self.humble_file_size
            chunk_size = ConfigData.chunk_size

            for chunk in web_request.iter_content(chunk_size=chunk_size):
                read_bytes += chunk_size
                read_bytes = min(total_length, read_bytes)

                current_percentage = Events.check_percent(
                        read_bytes, total_length, current_percentage)

                if chunk:
                    f.write(chunk)
                    f.flush()

    def __create_directory(self):
        """ Creates the directory for storing the current file if it doesn't
            exist.
        """

        # TODO HK: add options for path structure from commandline and or cfg file

        # full_directory = os.path.join(ConfigData.download_location,
        #                               self.order_number, self.subproduct_name, self.platform)

        if not ConfigData.folderstructure_OrderName:
            full_directory = os.path.join(ConfigData.download_location,
            				              self.subproduct_name, self.platform)
        else:
            full_directory = os.path.join(ConfigData.download_location,
                                          self.product_name_machine, self.subproduct_name, self.platform)


        if not os.path.exists(full_directory):
            os.makedirs(full_directory)

    def is_valid(self):
        if self.humble_file_size is None or self.humble_file_size == 0:
            self.status_message = ("Humble file size reported as 0. "
                                   "Download is invalid.")
            return False
        if self.download_url is None or len(self.download_url) == 0:
            self.status_message = ("Humble download URL is an empty string. "
                                   "Download is invalid.")
            return False
        if self.humble_md5 is None or len(self.humble_md5) == 0:
            self.status_message = ("Humble MD5 is an empty string. "
                                   "Download is invalid.")
            return False
        if self.filename is None or len(self.filename) == 0:
            self.status_message = ("Filename is an empty string. "
                                   "Download is invalid.")
            return False

        return True

    def status(self):
        if not self.is_valid():
            return self.status_message

        object_dump = "order_number: %s\n" % self.order_number
        object_dump += "humble_md5: %s\n" % self.humble_md5
        object_dump += "local_md5: %s\n" % self.local_md5
        object_dump += "filename: %s\n" % self.filename
        object_dump += "platform: %s\n" % self.platform
        object_dump += "product_name: %s\n" % self.product_name
        object_dump += "full_filename: %s\n" % self.full_filename
        object_dump += "filename: %s\n" % self.filename
        object_dump += "platform: %s\n" % self.platform
        object_dump += "product_name: %s\n" % self.product_name
        object_dump += "product_name_machine: %s\n" % self.product_name_machine
        object_dump += "subproduct_name: %s\n" % self.subproduct_name
        object_dump += "download_url: %s\n" % self.download_url
        object_dump += "humble_file_size: %s\n" % self.humble_file_size
        object_dump += ("humble_file_size_human: %s\n" %
                        self.humble_file_size_human)
        object_dump += "local_file_size: %d\n" % self.local_file_size
        object_dump += "machine_name: %s\n" % self.machine_name
        object_dump += "status_message: %s\n" % self.status_message
        object_dump += "requires_download: %s\n" % self.requires_download
        object_dump += "partial_download: %s\n" % self.partial_download

        return object_dump.encode("utf-8")

    @staticmethod
    def update_download_list_url(hapi, hd_list):
        """Updates the download urls from a list"""
        keys = set(hd.order_number for hd in hd_list)
        for key in keys:  # Group by key to limit the number of requests
            updated_hd_list = HumbleDownload.downloads_from_key(hapi, key)
            # Iterate over HumbleDownload objects that have the same key
            for hd in [hd_k for hd_k in hd_list if hd_k.order_number == key]:
                # Update the urls of products based on their md5
                hd.download_url = [nhd.download_url for nhd in updated_hd_list
                                   if nhd.humble_md5 == hd.humble_md5][0]

    @staticmethod
    def download_is_excluded(platform, filename):
        """Returns a boolean value representing if the file is excluded by configuration"""
        if platform is "audio":
            if "flac" in filename:
                return not ConfigData.audio_types.get("flac", True)
            elif "ogg" in filename:
                return not ConfigData.audio_types.get("ogg", True)
            elif "mp3" in filename:
                return not ConfigData.audio_types.get("mp3", True)
            else:
                return not ConfigData.audio_types.get("other", True)
        elif platform is "ebook":
            if "pdf" in filename:
                return not ConfigData.ebook_types.get("pdf", True)
            elif "mobi" in filename:
                return not ConfigData.ebook_types.get("mobi", True)
            elif "epub" in filename:
                return not ConfigData.ebook_types.get("epub", True)
            else:
                return not ConfigData.ebook_types.get("other", True)
        else:
            return False

    @staticmethod
    def downloads_from_key(hapi, key):
        """Returns a list of HumbleDownload objetcts from a key string"""
        humble_downloads = []
        current_order = hapi.get_order(key)
        logger.display_message(False, "Processing",
            "{0} is product: {1}".format(key, current_order.product.human_name))
        for current_subproduct in current_order.subproducts or []:
            for current_download in current_subproduct.downloads or []:
                if not ConfigData.download_platforms.get(
                        current_download.platform, False):
                    continue
                for current_dl_struct in current_download.download_structs:
                    if HumbleDownload.download_is_excluded(current_download.platform, current_dl_struct.filename):
                        print("skipping excluded download: " +
                              current_dl_struct.filename)
                        continue
                    hd = HumbleDownload(current_download,
                                        current_dl_struct,
                                        current_order,
                                        current_subproduct,
                                        key)
                    if hd.is_valid():
                        humble_downloads.append(hd)
        return humble_downloads

    @staticmethod
    def needed_downloads_from_key(hapi, key):
        """Returns a list of HumbleDownload objetcts corresponding to items
        that have not been already downloaded, from a key string"""
        humble_downloads = []
        for download in HumbleDownload.downloads_from_key(hapi, key):
            if not download.check_status():  # If not already downloaded
                humble_downloads.append(download)
        return humble_downloads
