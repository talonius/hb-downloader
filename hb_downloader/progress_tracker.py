#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from hb_downloader import logger

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2020 Brian Schkerke"
__license__ = "MIT"

import time
start_time = None

class ProgressTracker(object):
    """
        Helps with tracking progress, and determining what to output, when.
    """
    # TODO:  Make this class' output resemble wget/curl.
    
    item_count_current = 0
    item_count_total = 0

    download_size_current = 0
    download_size_total = 0

    current_product = ""
    current_subproduct = ""
    current_download = ""

    @staticmethod
    def assign_download(hd):
        """
            Translates a Humble Download object to a tracked download.
            
            :param hd: The Humble Download to be tracked.
        """
        ProgressTracker.current_product = hd.product_name
        ProgressTracker.current_subproduct = hd.subproduct_name
        ProgressTracker.current_download = hd.machine_name

    @staticmethod
    def display_summary():
        """
            Displays the current tracked download's progress.
        """
        global start_time
        if start_time:
            elapsed = time.time() - start_time
            fasts = ProgressTracker.download_size_current / elapsed
            remaining = (ProgressTracker.download_size_total - ProgressTracker.download_size_current) / fasts
        else:
            start_time = time.time()
            remaining = None
            fasts = 1024**2

        progress_message = "%d/%d DL: %s/%s (%s, %s)" % (
                ProgressTracker.item_count_current,
                ProgressTracker.item_count_total,
                ProgressTracker.format_filesize(
                        ProgressTracker.download_size_current),
                ProgressTracker.format_filesize(
                        ProgressTracker.download_size_total),
                ProgressTracker.format_percentage(
                        ProgressTracker.download_size_current,
                        ProgressTracker.download_size_total),
                ProgressTracker.format_seconds(remaining, ProgressTracker.download_size_total, fasts))

        logger.display_message(False, "Progress", progress_message)
        logger.display_message(
                True, "Progress", "%s: %s: %s" %
                (ProgressTracker.current_product,
                 ProgressTracker.current_subproduct,
                 ProgressTracker.current_download))

    @staticmethod
    def reset():
        """
            Resets all of the progress trackers.
        """
        ProgressTracker.item_count_total = 0
        ProgressTracker.item_count_current = 0
        ProgressTracker.download_size_current = 0
        ProgressTracker.download_size_total = 0
        ProgressTracker.current_product = ""
        ProgressTracker.current_subproduct = ""
        ProgressTracker.current_download = ""

    @staticmethod
    def format_filesize(filesize):
        """
            Translates a filesize into "human readable" format.
            
            :param filesize: The filesize to be converted.
        """
        prefixes = [' bytes', ' KiB', ' MiB', ' GiB', ' TiB']
        index_level = 0

        while abs(filesize / 1024) > 1 and index_level < len(prefixes) - 1:
            index_level += 1
            filesize /= 1024

        try:
            size = "%.2f%s" % (filesize, prefixes[index_level])
        except:
            size = "unknown"
            pass
        return size

    @staticmethod
    def format_seconds(seconds, bytecount, speed):
        """
            
            :param seconds:
            :param bytecount:
            :param speed:
        """
        if not seconds:
            return ProgressTracker.format_seconds(bytecount / speed, 1, speed) + f" estimated @ {ProgressTracker.format_filesize(speed)}/s"
        seconds = int(seconds)
        if seconds < 90:
            return f"{seconds}s left @ {ProgressTracker.format_filesize(speed)}/s"
        minutes = int(seconds / 60)
        seconds %= 60
        if minutes < 90:
            return f"{minutes}m {seconds}s left @ {ProgressTracker.format_filesize(speed)}/s"
        hours = int(minutes / 60)
        minutes %= 60
        if hours < 30:
            return f"{hours}h {minutes}m left @ {ProgressTracker.format_filesize(speed)}/s"
        days = int(hours / 24)
        hours %= 24
        if days < 7:
            return f"{days}d {hours}h {minutes}m left @ {ProgressTracker.format_filesize(speed)}/s"
        weeks = int(days / 7)
        if weeks < 3:
            days %= 7
            return f"{weeks}w {days}d {hours}h left @ {ProgressTracker.format_filesize(speed)}/s"
        months = int(days / 30)
        if months < 15:
            days %= 30
            return f"{months}m {days}d left @ {ProgressTracker.format_filesize(speed)}/s"
        years = int(days / 365)
        days %= 365
        return f"{years}y {days}d left @ {ProgressTracker.format_filesize(speed)}/s"

    @staticmethod
    def format_percentage(current, total):
        """
            Formats a percentage based on the current vs. total byte count.
            
            :param current: The current number of bytes.
            :param total: The total number of bytes.
        """
        if total == 0:
            return "0.00%"
        else:
            return '{percent:.2%}'.format(percent=(1.0 * current)/total)
