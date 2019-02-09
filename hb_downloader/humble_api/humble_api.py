#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.cookiejar
import itertools
from .model.order import Order
import requests
from .exceptions.humble_response_exception import HumbleResponseException
from .exceptions.humble_parse_exception import HumbleParseException

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"

__all__ = ["HumbleApi"]


class HumbleApi(object):
    """
        This class represents common actions for the Humble API.

        The Humble Bundle API is not stateless, it stores an authentication token as a cookie named _simpleauth_sess

        The Requests.Session handles storing the auth token. To load some persisted cookies simply set session.cookies
        after initialization.
    """

    # URLs.
    LOGIN_URL = "https://www.humblebundle.com/processlogin"
    ORDER_LIST_URL = "https://www.humblebundle.com/api/v1/user/order"
    ORDER_URL = "https://www.humblebundle.com/api/v1/order/{order_id}"

    # default_headers specifies the default HTTP headers added to each request sent to the humblebundle.com servers.
    default_headers = {
        "Accept": "application/json",
        "Accept-Charset": "utf-8",
        "Keep-Alive": "true",
        "X-Requested-By": "hb_android_app",
        "User-Agent": "Apache-HttpClient/UNAVAILABLE (java 1.4)"
    }

    # default_params specifies the default querystring parameters added to each
    # request sent to humblebundle.com.
    default_params = {"ajax": "true"}

    def __init__(self, auth_sess_cookie):
        """
            Base constructor.  Responsible for setting up the requests object
            and cookie jar. All configuration values should be set prior to
            constructing an object of this type; changes to configuration will
            not take effect on variables which already exist.
        """
        self.session = requests.Session()

        auth_sess_cookie = bytes(
                auth_sess_cookie, "utf-8").decode("unicode_escape")
        cookie = http.cookiejar.Cookie(
                0, "_simpleauth_sess", auth_sess_cookie, None, None,
                "www.humblebundle.com", None, None, "/", None, True,
                None, False, None, None, None)
        self.session.cookies.set_cookie(cookie)

        self.session.headers.update(self.default_headers)
        self.session.params.update(self.default_params)

    def check_login(self):
        """
            Checks to see if we have a valid session cookie by attempting to retrieve the orders page.
            If we get a HumbleAuthenticationException then we need to log in to the system again.
            Otherwise we're good to go.

            We can't just check for the cookie existence.  The session ID might've been
            invalidated server side.

            :return: True if the _simpleauth_sess cookie has been set, False if not.
        """
        try:
            gamekeys = self.get_gamekeys()
            if len(gamekeys) > 0:
                return True
            else:
                return False
        except HumbleAuthenticationException:
            return False

    def get_gamekeys(self, *args, **kwargs):
        """
            Fetch all the gamekeys owned by an account.

            A gamekey is a string that uniquely identifies an order from the Humble store.

            :param list args: (optional) Extra positional args to pass to the request
            :param dict kwargs: (optional) Extra keyword args to pass to the request
            :return: A list of gamekeys
            :rtype: list
            :raises RequestException: if the connection failed
            :raises HumbleAuthenticationException: if not logged in
            :raises HumbleResponseException: if the response was invalid
        """
        response = self._request("GET", HumbleApi.ORDER_LIST_URL, *args, **kwargs)

        """ get_gamekeys response always returns JSON """
        data = self.__parse_data(response)

        if isinstance(data, list):
            return [v["gamekey"] for v in data]

        # Let the helper function raise any common exceptions
        self.__authenticated_response_helper(response, data)

        # We didn't get a list, or an error message
        raise HumbleResponseException("Unexpected response body", request=response.request, response=response)

    def get_order(self, order_id, *args, **kwargs):
        """
            Download an order by its ID.

            :param order_id: The identifier ("gamekey") that uniquely identifies the order
            :param list args: (optional) Extra positional args to pass to the request
            :param dict kwargs: (optional) Extra keyword args to pass to the request
            :return: The :py:class:`Order` requested
            :rtype: Order
            :raises RequestException: if the connection failed
            :raises HumbleAuthenticationException: if not logged in
            :raises HumbleResponseException: if the response was invalid
        """
        url = HumbleApi.ORDER_URL.format(order_id=order_id)

        response = self._request("GET", url, *args, **kwargs)

        """ order response might be 404 with no body if not found """

        if response.status_code == requests.codes.not_found:
            raise HumbleResponseException("Order not found", request=response.request, response=response)

        data = self.__parse_data(response)

        # The helper function should be sufficient to catch any other errors
        if self.__authenticated_response_helper(response, data):
            return Order(data)

    def _request(self, *args, **kwargs):
        """
            Set sane defaults that aren't session wide. Otherwise maintains the API of Session.request.

            :param list args: (optional) Extra positional args to pass to the request.
            :param dict kwargs: (optional) Extra keyword args to pass to the request.
        """
        kwargs.setdefault("timeout", 30)
        return self.session.request(*args, **kwargs)

    def __authenticated_response_helper(self, response, data):
        """
            Checks a response for the common authentication errors.  Sometimes a successful API call won't have a
             success property.  We do a check for this property and return true if found, otherwise we parse for
s             errors.

            :param response:  The response received from humblebundle.com. A pass through variable used to initialize
             the exceptions.
            :param data:  The interpreted JSON data from the response.
            :return:  True if the API call was successful.  Otherwise an exception is thrown.
            :raises HumbleAuthenticationException: If not logged in.
            :raises HumbleResponseException: If the response was invalid.
        """
        success = data.get("success", None)
        if success:
            return True

        error_id = data.get("error_id", None)
        errors, error_msg = self.__get_errors(data)

        # API calls that require login and have a missing or invalid token.
        if error_id == "login_required":
            raise HumbleAuthenticationException(error_msg, request=response.request, response=response)

        # Something happened, we're not sure what but we hope the error_msg is useful.
        if success is False or errors is not None or error_id is not None:
            raise HumbleResponseException(error_msg, request=response.request, response=response)

        # Response had no success or errors fields, it's probably data
        return True

    def __parse_data(self, response):
        """
            Try and parse the response data as JSON.  If parsing fails, throw a HumbleParseException.

            :param response:  The response received from humblebundle.com.
             A pass through variable used to initialize the exceptions.
            :return:  The response as a JSON object.
            :raises HumbleParseException:  When the response cannot be parsed as a JSON object.
        """
        try:
            return response.json()
        except ValueError as e:
            raise HumbleParseException("Invalid JSON: %s", str(e), request=response.request, response=response)

    def __get_errors(self, data):
        """
            Retrieves any errors defined within the JSON and returns them as a string.

            :param data: The JSON data to be searched for errors.
            :return:  A tuple containing the errors and error message.
        """
        errors = data.get("errors", None)
        error_msg = ", ".join(itertools.chain.from_iterable(v for k, v in list(errors.items()))) \
            if errors else "Unspecified error"
        return errors, error_msg
