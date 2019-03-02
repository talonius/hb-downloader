#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import os
from .events import Events

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2016 Brian Schkerke"
__license__ = "MIT"

__all__ = ["HumbleHash"]


class HumbleHash(object):
    """
        HumbleHash is the central repository for all code related to calculating and maintaining
        MD5 checksums for the Humble Bundle downloader.
    """
    chunk_size = 8192000
    force_md5 = False
    write_md5 = True
    read_md5 = True

    @staticmethod
    def calculate_checksum(full_filename):
        """
            Calculates the MD5 checksum for the given file and returns the hex representation.

            :param full_filename: The full path and filename of the file to calculate the MD5 for.
            :return: The hex representation of the MD5 hash.
            :rtype: str
        """
        if full_filename is None or not os.path.exists(full_filename):
            return ""

        current_percentage = 0

        with open(full_filename, "rb") as f:
            total_length = os.path.getsize(full_filename)
            read_bytes = 0

            Events.trigger(Events.EVENT_MD5_START, full_filename)

            md5_hash = hashlib.md5()
            while True:
                data = f.read(HumbleHash.chunk_size)
                read_bytes += HumbleHash.chunk_size
                read_bytes = min(total_length, read_bytes)

                if not data:
                    break

                md5_hash.update(data)
                current_percentage = Events.check_percent(read_bytes, total_length, current_percentage)

            Events.trigger(Events.EVENT_MD5_END, full_filename)
            HumbleHash.write_md5file(full_filename, md5_hash.hexdigest())
            return md5_hash.hexdigest()

    @staticmethod
    def checksum(full_filename):
        """
            Retrieves or calculates the checksum for the given filename.  First checks for the
            existence of an MD5 file and reads the MD5 value from it, if possible.  Otherwise it
            calculates the checksum of the given file and returns the value.

            :param full_filename: The full path and filename of the file to calculate and compare the MD5 hash for.
            :return: The MD5 checksum of the provided path and filename as a string.
            :rtype: string
        """
        if full_filename is None or not os.path.exists(full_filename):
            return ""

        stored_checksum = HumbleHash.read_md5file(full_filename)
        if len(stored_checksum) == 0:
            stored_checksum = HumbleHash.calculate_checksum(full_filename)

        return stored_checksum

    @staticmethod
    def verify_checksum(full_filename, checksum):
        """
            Compares the checksum for the given filename against the given checksum.  First checks for the
            existence of an MD5 file and reads the MD5 value from it, if possible.  Otherwise it
            calculates the checksum of the given file and returns whether it matches the provided hash.

            :param full_filename: The full path and filename of the file to calculate and compare the MD5 hash for.
            :param checksum: The MD5 hash we're comparing the file against; generally read from humblebundle.com.
            :return: True if the MD5 hash of the given file matches the provided md5_hash.
            :rtype: bool
        """
        stored_checksum = HumbleHash.checksum(full_filename)
        return stored_checksum == checksum, stored_checksum

    @staticmethod
    def remove_md5file(full_filename):
        """
            Removes an MD5 file from storage.

            :param full_filename: The full path and filename of the file to remove the MD5 checksum for.
        """
        if full_filename is None or not os.path.exists(full_filename):
            return

        md5full_filename = HumbleHash.md5filename(full_filename)

        if os.path.exists(md5full_filename):
            os.remove(md5full_filename)

    @staticmethod
    def read_md5file(full_filename):
        """
            Reads an MD5 hash from an MD5 file.

            :param full_filename:  The full path and filename of the file to attempt to read the MD5 file.
            :return:  The MD5 value read, or an empty string if no file was found or its format was invalid.
        """
        if full_filename is None or not os.path.exists(full_filename) or not HumbleHash.read_md5:
            return ""

        md5full_filename = HumbleHash.md5filename(full_filename)
        local_filename = os.path.basename(md5full_filename)

        if not os.path.exists(md5full_filename):
            return ""

        md5line = None

        with open(md5full_filename, "r") as f:
            for line in f:
                if line.endswith(local_filename):
                    md5line = line
                    break

        if md5line is None or len(md5line) == 0:
            return ""
        else:
            return md5line[0:32]

    @staticmethod
    def write_md5file(full_filename, checksum):
        """
            Writes an MD5 file for a given filename.  If md5_hash is not provided the hash
            will be calculated prior to write.

            :param str full_filename: The full path and filename of the file to create an MD5 file for.
            :param str checksum: The MD5 hash value of the given file, if known.
            :return: None
        """
        if not HumbleHash.write_md5:
            return

        if full_filename is None:
            return

        md5full_filename = HumbleHash.md5filename(full_filename)
        local_filename = os.path.basename(full_filename)

        if os.path.exists(md5full_filename):
            os.remove(md5full_filename)

        if checksum is None:
            checksum = HumbleHash.calculate_checksum(full_filename)

        with open(md5full_filename, "wb") as f:
            f.write((checksum + " *%s" % local_filename).encode())

    @staticmethod
    def md5filename(full_filename):
        """
            Calculates and returns the MD5 filename for a given file.

            :param full_filename:  The full path and filename of the file to calculate the MD5 location for.
            :return: A string representing the MD5 filename for the given file.
            :rtype: str
            :raise ValueError:  If full_filename is not specified upon function execution.
        """
        if full_filename is None or len(full_filename) == 0:
            raise ValueError("full_filename must be specified in call to md5filename.")

        full_filename += ".md5"
        return full_filename
