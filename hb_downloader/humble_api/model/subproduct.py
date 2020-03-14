#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .base_model import BaseModel
from .payee import Payee
from .download import Download

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class Subproduct(BaseModel):
    """
        Represents a subproduct.  For example, the Snuggletruck soundtrack and
        the Snuggletruck game would be subproducts of Humble Bundle 2.

        machine_name:  The name of the subproduct as usable on a PC.
        url:  The web page associated with the subproduct.  Not the download URL.
        platform:  The recipient(s) of the funds for this subproduct.
        downloads:  The downloads associated with this subproduct.
        human_name:  The human readable name for the subproduct.
        custom_download_page_box_html:  This is used to popup messages about the subproduct
         related to the download.  For instance, 'This requires UPlay." or "This requires Steam."
        icon:  The icon to be displayed for the subproduct.
    """

    def __init__(self, data, get_extra_file_info=False):
        """
            Parameterized constructor for the Subproduct object.

            :param client: The client which is defining the object.
            :param data: The JSON data to define the object with.
        """
        super(Subproduct, self).__init__(data)

        self.machine_name = data.get("machine_name", None)
        self.url = data.get("url", None)
        self.payee = Payee(data["payee"])
        self.downloads = [Download(download, get_extra_file_info) for download in data["downloads"]]
        self.human_name = data.get("human_name", None)
        self.custom_download_page_box_html = data.get("custom_download_page_box_html", None)
        self.icon = data.get("icon", None)
        self.platform = data.get("platform", None)
        self.product_name = self.__determine_product_name()

    def __determine_product_name(self):
        """
            Determines the name of the product to be used when saving files to the local file system.

            :return: The product name.
            :rtype: str
        """
        if self.machine_name is None or len(self.machine_name) == 0:
            return ""

        return_value = self.machine_name

        if return_value.endswith("withsoundtrack"):
            return_value = return_value.replace("withsoundtrack", "")

        underscore_index = return_value.find("_")
        if underscore_index != -1:
            return_value = return_value[0:underscore_index]

        return return_value

    def __repr__(self):
        """ Representation of a Subproduct object. """
        return "Subproduct: <%s>" % self.machine_name
