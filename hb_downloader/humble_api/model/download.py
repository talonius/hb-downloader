#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .base_model import BaseModel
from .download_struct import DownloadStruct

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class Download(BaseModel):
    """
        Represents a download for an Subproduct.

        machine_name:  The name of the subproduct as usable on a PC.
        platform:  The platform of the download.  (audio, asmjs, etc.)
        options_dict:
        download_identifier:  Appears to be the Android package name for the download.
        download_version_number:  A numeric representation of the version of the application the download represents.
        android_app_only:
        download_structs:  The definitions of the actual download locations.
    """

    def __init__(self, data, get_extra_file_info=False):
        """
            Parameterized constructor for the Download object.

            :param data: The JSON data to define the object with.
        """
        super(Download, self).__init__(data)

        self.machine_name = data.get("machine_name", None)
        self.platform = data.get("platform", None)
        self.download_structs = [DownloadStruct(struct, get_extra_file_info) for struct in data["download_struct"]]
        self.options_dict = data["options_dict"]
        self.download_identifier = data.get("download_identifier", None)
        self.download_version_number = data.get("download_version_number", None)
        self.android_app_only = data.get("android_app_only", False)

    def __repr__(self):
        return "Download: <%s>" % self.machine_name
