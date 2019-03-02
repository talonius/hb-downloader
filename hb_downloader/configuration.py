#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import os
import yaml
from urllib.parse import urlparse
from urllib.parse import parse_qs
from hb_downloader import logger
from hb_downloader.config_data import ConfigData
from hb_downloader.humble_api.humble_hash import HumbleHash

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2016 Brian Schkerke"
__license__ = "MIT"


class Configuration(object):
    cmdline_platform = {}  # Mapping between hb convention and ours

    @staticmethod
    def init_platforms():
        c = Configuration.cmdline_platform
        c['games'] = ['android', 'asmjs', 'linux', 'mac', 'windows']
        c['ebooks'] = ['ebook']
        c['audio'] = ['audio']
        c['all'] = c['games'] + c['ebooks'] + c['audio']

    @staticmethod
    def validate_configuration():
        """
            Does a basic validation of the configuration to ensure we're not
            missing anything critical.

            :return:  None
        """
        if not os.path.exists(ConfigData.download_location):
            return False, "Download location doesn't exist"

        if not os.access(ConfigData.download_location, os.W_OK | os.X_OK):
            return False, (
                    "Download location is not writable by the current user.")

        return True, ""

    @staticmethod
    def load_configuration(config_file):
        """
            Loads configuration data from a yaml file.

            :param config_file:  The yaml file to load configuration data from.
            :return:  None
        """
        with open(config_file, "r") as f:
            saved_config = yaml.safe_load(f)

        ConfigData.download_platforms = saved_config.get(
                "download-platforms", ConfigData.download_platforms)
        ConfigData.write_md5 = saved_config.get(
                "write_md5", ConfigData.write_md5)
        ConfigData.read_md5 = saved_config.get(
                "read_md5", ConfigData.read_md5)
        ConfigData.force_md5 = saved_config.get(
                "force_md5", ConfigData.force_md5)
        ConfigData.chunk_size = saved_config.get(
                "chunksize", ConfigData.chunk_size)
        ConfigData.debug = saved_config.get(
                "debug", ConfigData.debug)
        ConfigData.download_location = saved_config.get(
                "download-location", ConfigData.download_location)
        ConfigData.auth_sess_cookie = saved_config.get(
                "session-cookie", ConfigData.auth_sess_cookie)
        ConfigData.resume_downloads = saved_config.get(
                "resume_downloads", ConfigData.resume_downloads)
        ConfigData.ignore_md5 = saved_config.get(
                "ignore_md5", ConfigData.ignore_md5)

    @staticmethod
    def parse_command_line():
        """
            Parses configuration options from the command line arguments to the
            script.

            :return:  None
        """
        parser = argparse.ArgumentParser()

        parser.add_argument("-d", "--debug", action="store_true",
                            default=ConfigData.debug,
                            help="Activates debug mode.")
        parser.add_argument("-dl", "--download_location",
                            default=ConfigData.download_location, type=str,
                            help="Location to store downloaded files.")
        parser.add_argument(
                "-cs", "--chunksize", default=ConfigData.chunk_size, type=int,
                help=("The size to use when calculating MD5s and downloading"
                      "files."))
        parser.add_argument(
                "-c", "--auth_cookie",
                default=ConfigData.auth_sess_cookie, type=str,
                help="The _simple_auth cookie value from a web browser")

        sub = parser.add_subparsers(
                title="action", dest="action",
                help=("Action to perform, optionally restricted to a few "
                      "specifiers. If no action is specified, the tool "
                      "defaults to downloading according to the configuration "
                      "file. Please note that specifying an action WILL"
                      "override the configuration file."))

        a_list = sub.add_parser("list", help=(
                "Display library items in a tab-separated tree-like structure "
                "that can be parsed as a CSV."))
        a_download = sub.add_parser(
                "download", help=(
                        "Download specific items from the library instead of "
                        "the ones specified in the configuration file. This "
                        "is the default action, but specifying it will "
                        "override the configuration file. If no further "
                        "parameters are specified, this will default to "
                        "downloading everything in the library."))
        a_product = sub.add_parser(
                "download-product", help=(
                        "You can narrow downloading down to the product level. "
                        "This would be one single bundle. "))

        a_product.add_argument(
            dest="download_product",
            help="Product Key (looks like a bunch of garbled letters)"
            )

        for action in [a_list, a_download]:
            item_type = action.add_subparsers(title="type", dest="item_type")
            games = item_type.add_parser("games")
            games.add_argument(
                    "--platform", nargs='+', choices=[  # TODO: add NATIVE?
                            "linux", "mac", "windows", "android", "asmjs"])
            item_type.add_parser("ebooks")
            item_type.add_parser("audio")
            item_type.add_parser("all")

        a_list.add_argument(
                "-u", "--print-url", action="store_true", dest="print_url",
                help=("Print the download url with the output. Please note "
                      "that the url expires after a while"))
        args = parser.parse_args()

        Configuration.configure_action(args)

        ConfigData.debug = args.debug

        ConfigData.download_location = args.download_location
        ConfigData.chunk_size = args.chunksize
        ConfigData.auth_sess_cookie = args.auth_cookie

    @staticmethod
    def configure_action(args):
        if "platform" not in dir(args):
            args.platform = None
        if "print_url" not in dir(args):
            args.print_url = False

        if args.action is not None:
            if args.action == "download-product":
                args.platform = None
                ConfigData.download_product = args.download_product
                url = urlparse(args.download_product)
                qs = parse_qs(url.query)
                if qs and qs['key']:
                    ConfigData.download_product = qs['key'][0]

            elif args.platform is None:
                args.platform = Configuration.cmdline_platform.get(
                        args.item_type)
            for platform in ConfigData.download_platforms:
                if args.platform is None:
                    ConfigData.download_platforms[platform] = True
                    continue
                if platform in args.platform:
                    ConfigData.download_platforms[platform] = True
                else:
                    ConfigData.download_platforms[platform] = False
        else:
            args.action = "download"
        ConfigData.action = args.action
        ConfigData.print_url = args.print_url

    @staticmethod
    def dump_configuration():
        """
            Dumps the current configuration to the log when debug mode is
            activated
            :return: None
        """
        # Shortcut the process if debugging is not turned on.
        if not ConfigData.debug:
            return

        logger.display_message(
                True, "Config", "write_md5=%s" % ConfigData.write_md5)
        logger.display_message(
                True, "Config", "read_md5=%s" % ConfigData.read_md5)
        logger.display_message(
                True, "Config", "force_md5=%s" % ConfigData.force_md5)
        logger.display_message(
                True, "Config", "ignore_md5=%s" % ConfigData.ignore_md5)
        logger.display_message(
                True, "Config", "debug=%s" % ConfigData.debug)
        logger.display_message(
                True, "Config", "download_location=%s" %
                ConfigData.download_location)
        logger.display_message(
                True, "Config", "chunksize=%s" % ConfigData.chunk_size)
        logger.display_message(
                True, "Config", "resume_downloads=%s" %
                ConfigData.resume_downloads)

        for platform in list(ConfigData.download_platforms.keys()):
            logger.display_message(
                    True, "Config", "Platform %s=%s" %
                    (platform, ConfigData.download_platforms[platform]))

    @staticmethod
    def push_configuration():
        """
            Pushes configuration variables down to lower libraries which
            require them.

            :return: None
        """
        HumbleHash.write_md5 = ConfigData.write_md5
        HumbleHash.read_md5 = ConfigData.read_md5
        HumbleHash.force_md5 = ConfigData.force_md5
        HumbleHash.chunk_size = ConfigData.chunk_size

Configuration.init_platforms()
