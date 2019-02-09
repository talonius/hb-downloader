#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Joel Pedraza"
__copyright__ = "Copyright 2014, Joel Pedraza"
__license__ = "MIT"


class BaseModel(object):
    """
        Represents the base object used by all of the Humble Bundle objects.
    """

    def __init__(self, data):
        """
            Parameterized constructor for the BaseModel object.

            :param data: The JSON data to define the object with.
        """
        self._data = data

    def __unicode__(self):
        """
            Called by the str() built-in function and by the print statement to compute the
            "informal" string representation of an object.
        """
        return str(self).encode("utf-8")

    def __str__(self):
        """
            Called by the str() built-in function and by the print statement to compute the
            "informal" string representation of an object encoded as ASCII.
        """
        return str({key: self.__dict__[key] for key in self.__dict__ if key != "_client"})

    def __repr__(self):
        """
            Called by the repr() built-in function and by string conversions (reverse quotes) to
            compute the "official" string representation of an object. If at all possible, this
            should look like a valid Python expression that could be used to recreate an object
            with the same value (given an appropriate environment).
        """
        return repr(self.__dict__)

    def __iter__(self):
        """
           If a container object's __iter__() method is implemented as a generator, it will
           automatically return an iterator object (technically, a generator object) supplying
           the  __iter__() and next() methods.
        """
        return self.__dict__.__iter__()
