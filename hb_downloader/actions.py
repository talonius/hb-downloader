#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__license__ = "MIT"

from hb_downloader.humble_download import HumbleDownload
from hb_downloader.progress_tracker import ProgressTracker
from hb_downloader.config_data import ConfigData
from hb_downloader import logger


class Action:
    @staticmethod
    def list_downloads(hapi, game_keys):
        for key in game_keys:
            selector_matched_key_once = False
            current_order = hapi.get_order(key, ConfigData.get_extra_file_info)

            for current_subproduct in current_order.subproducts or []:
                selector_matched_subproduct_once = False
                for current_download in current_subproduct.downloads or []:
                    if not ConfigData.download_platforms.get(
                            current_download.platform, False):
                        continue
                    if not selector_matched_key_once:
                        selector_matched_key_once = True
                        print(
                            "%s\t(%s)\t%s\t%s" %
                             (current_order.product.human_name, key,
                              current_order.product.category,
                              current_order.product.machine_name))
                    if not selector_matched_subproduct_once:
                        selector_matched_subproduct_once = True
                        print("\t%s" % current_subproduct.human_name)
                    for dl_struct in current_download.download_structs:
                        string = "\t\t%s\t%s\t%s\t%s\t%s" % (
                                current_download.platform,
                                current_download.machine_name,
                                dl_struct.name,
                                dl_struct.human_size,
                                dl_struct.timestamp)
                        if ConfigData.get_extra_file_info:
                            string = "%s\t%s" % (string,
                                                 dl_struct.last_modified)
                        if ConfigData.print_url:
                            string = "%s\t%s" % (string,
                                                 dl_struct.download_web)
                        print(string)

    @staticmethod
    def batch_download(hapi, game_keys):
        ProgressTracker.reset()
        ProgressTracker.item_count_total = len(game_keys)
        download_size_total = 0
        item_count_total = 0
        key_downloads = dict()
        # Create initial list of Humble Downloads.
        # Platforms that are turned off are filtered here, and the download
        # size is computed. Checksums are also calculated for finished
        # downloads. This initial query could be paralelized for speed gains
        for key in game_keys[::-1]:
            ProgressTracker.item_count_current += 1
            logger.display_message(
                    False, "Processing",
                    "Retrieving order details for order %s (%d/%d)." %
                    (key, ProgressTracker.item_count_current,
                     ProgressTracker.item_count_total))

            humble_downloads = HumbleDownload.needed_downloads_from_key(hapi,
                                                                        key)
            item_count_total += len(humble_downloads)
            download_size_total += sum(
                    dl.humble_file_size for dl in humble_downloads)
            logger.display_message(False, "Processing",
                                   "Added %d downloads for order %s"
                                   % (len(humble_downloads), key))

            if len(humble_downloads) > 0:
                key_downloads[key] = humble_downloads

        ProgressTracker.reset()
        ProgressTracker.item_count_total = item_count_total
        ProgressTracker.download_size_total = download_size_total

        # Now, download the files after updating the url in case they expired
        for key in key_downloads:
            HumbleDownload.update_download_list_url(
                    hapi, key_downloads.get(key))
            for hd in key_downloads.get(key):
                ProgressTracker.assign_download(hd)
                ProgressTracker.display_summary()
                logger.display_message(False, "Download", hd.status_message)
                logger.display_message(
                        False, "Download",
                        "Downloading %s." % hd.humble_file_size_human)
                hd.download_file()

                if hd.humble_file_size is not None:
                    ProgressTracker.download_size_current += (
                            hd.humble_file_size)
                ProgressTracker.item_count_current += 1

        logger.display_message(False, "Processing", "Finished.")
