#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .humble_response_exception import HumbleResponseException

__license__ = "MIT"


class HumbleAuthenticationException(HumbleResponseException):
    """
        Authentication failed due to a rejected authentication cookie
    """

    def __init__(self, *args, **kwargs):
        """
            Parameterized constructor for the HumbleAuthenticationException.
            :param list args: (optional) Extra positional args to pass to the request.
            :param dict kwargs: (optional) Extra keyword args to pass to the request.
        """

        super(HumbleAuthenticationException, self).__init__(*args, **kwargs)
