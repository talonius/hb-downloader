#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .humble_response_exception import HumbleResponseException

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class HumbleDownloadNeededException(HumbleResponseException):
    """
        This exception is thrown when a downloaded file's MD5 fails
        the check or the file doesn't exist.
    """

    def __init__(self, message, *args, **kwargs):
        """
            Parameterized constructor.

            :param str message:  The message associated with the reason why a download is needed.
            :param list args: (optional) Extra positional args to pass to the request.
            :param dict kwargs: (optional) Extra keyword args to pass to the request.
        """
        super(HumbleDownloadNeededException, self).__init__(*args, **kwargs)

        self.message = message
