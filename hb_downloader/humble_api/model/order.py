#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .base_model import BaseModel
from .subscription import Subscription
from .subproduct import Subproduct
from .product import Product

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class Order(BaseModel):
    """
        Represents a single order (Weekly Bundle, Monthly Bundle, etc.) which itself contains a list of
        products which were a part of the order.
    """

    def __init__(self, data):
        """
            Parameterized constructor for the Order object.

            :param data: The JSON data to define the object with.
        """
        super(Order, self).__init__(data)

        self.product = Product(data["product"])
        subscriptions_json = data.get("subscriptions", [])
        self.subscriptions = \
            [Subscription(sub) for sub in subscriptions_json] \
            if len(subscriptions_json) > 0 else None

        self.created = data.get("created", None)
        self.amount_to_charge = data.get("amount_to_charge", None)
        self.gamekey = data.get("gamekey", None)
        self.subproducts = ([Subproduct(prod) for prod in data.get("subproducts", [])]) or None

        # Former fields that I couldn't locate in my output:
        #   thankname, claimed, country, giftee, leaderboard, owner_username

    def __repr__(self):
        """ Representation of an Order object. """
        return "Order: <%s>" % self.product.machine_name
