#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from .base_model import BaseModel

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class Product(BaseModel):
    """
        Represents a product from the storefront or from a bundle.

        category:
        machine_name:
        post_purchase_text:
        supports_canonical:
        human_name:
        partial_gift_enabled:
    """

    def __init__(self, data):
        """
            Parameterized constructor for the Product object.

            :param client: The client which is defining the object.
            :param data: The JSON data to define the object with.
        """
        super(Product, self).__init__(data)

        self.category = data.get("category", None)
        self.machine_name = data.get("machine_name", None)
        self.post_purchase_text = data.get("post_purchase_text", None)
        self.supports_canonical = data.get("supports_canonical", None)
        self.human_name = data.get("human_name", None)
        self.partial_gift_enabled = data.get("partial_gift_enabled", False)

    def __repr__(self):
        """ Representation of a Product object. """
        return "Product: <%s>" % self.machine_name
