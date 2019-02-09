#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .base_model import BaseModel

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class Subscription(BaseModel):
    """
        Represents a subscription purchased through the Humble Bundle.

        A Humble Monthly subscription does not appear under this.

        human_name:  The human readable name of the subscription.
        list_name:
        subscribed:
    """

    def __init__(self, data):
        """
            Parameterized constructor for the Subscription object.

            :param client: The client which is defining the object.
            :param data: The JSON data to define the object with.
        """
        super(Subscription, self).__init__(data)

        self.human_name = data.get("human_name", None)
        self.list_name = data.get("list_name", None)
        self.subscribed = data.get("subscribed", None)

    def __repr__(self):
        """ Representation of the current Subscription object. """
        return "Subscription: <%s : %s>" % (self.list_name, self.subscribed)
