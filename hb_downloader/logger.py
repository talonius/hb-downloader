#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from hb_downloader.config_data import ConfigData
import time
import sys

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2016 Brian Schkerke"
__license__ = "MIT"


def display_message(is_debug, category, user_message, add_crlf=True):
    """
        Centralized function for dumping data to the console.

        :param is_debug:  Whether this is a debug message or normal message.
        :param category:  The category to print for the message.
        :param user_message:  The user message to print after the message.
        :param add_crlf:  Whether to append a carriage return to the printed
        message or not.
        :return:  None
    """
    assert isinstance(is_debug, bool)
    assert isinstance(category, str)
    assert isinstance(user_message, str)

    category_width = 10

    if (is_debug and ConfigData.debug) or not is_debug:
        formatted_message = ("[%s] [%s] %s" %
                             (time.strftime("%Y/%m/%d %I:%M:%S"),
                              category.rjust(category_width), user_message))
        if add_crlf:
            print(formatted_message)
        else:
            sys.stdout.write(formatted_message)
