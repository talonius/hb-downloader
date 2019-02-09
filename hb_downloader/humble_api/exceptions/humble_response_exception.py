#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
from .humble_exception import HumbleException

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class HumbleResponseException(requests.RequestException, HumbleException):
    """ A request completed but the response was somehow invalid or unexpected. """

    def __init__(self, *args, **kwargs):
        """
            Parameterized constructor for HumbleResponseException.

            :param list args: (optional) Extra positional args to pass to the request.
            :param dict kwargs: (optional) Extra keyword args to pass to the request.
        """
        super(HumbleResponseException, self).__init__(*args, **kwargs)
