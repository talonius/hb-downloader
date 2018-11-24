#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2016 Brian Schkerke"
__license__ = "MIT"


class Events(object):
    """
        The bare minimum of a static event handler.  Allows for global registration
        of callbacks to events as defined solely by string IDs.  The event handlers
        should have the function event_handler(object_type); the only argument passed
        to the callback is the object which instantiated the event.
    """
    _callbacks = None

    EVENT_MD5_START = "MD5_Start"
    EVENT_MD5_END = "MD5_End"
    EVENT_DOWNLOAD_START = "Download_Start"
    EVENT_DOWNLOAD_END = "Download_End"
    EVENT_PROGRESS = "Progress"

    @staticmethod
    def on(event_name, callback):
        """
            Subscribes to an event.

            :param str event_name: The name of the event to create a subscription for.
            :param callback: The function to be invoked when the event is triggered.
        """
        if event_name is None or len(event_name) == 0:
            return

        if callback is None:
            return

        if Events._callbacks is None:
            Events._callbacks = {}

        if event_name not in Events._callbacks:
            Events._callbacks[event_name] = [callback]
        else:
            Events._callbacks[event_name].append(callback)

    @staticmethod
    def trigger(event_name, callback_argument):
        """
            Triggers the specified event (as specified by event_name).

            :param callback_argument:  The argument to be passed to the subscribed functions.
            :param event_name:  The string name of the event being triggered.
        """
        if event_name is None or len(event_name) == 0:
            return

        if Events._callbacks is not None and event_name in Events._callbacks:
            for callback in Events._callbacks[event_name]:
                callback(callback_argument)

    @staticmethod
    def check_percent(current, total, current_percentage):
        """
            Checks whether the current progress exceeds the current percentage.  Used to determine whether
            an event should be fired.
            :param current:  The current progress in whatever proprietary format your heart desires.
            :param total:  The total progress in whatever proprietary format your heart desires.
            :param current_percentage:  The current progress percentage as last defined.
            :return:  The new value for the current_percentage, if it is modified.
        """
        percentage = current / total * 100
        percentage -= percentage % 0.01
        if current_percentage < percentage:
            current_percentage = percentage
            Events.trigger(Events.EVENT_PROGRESS, current_percentage)

        return current_percentage
