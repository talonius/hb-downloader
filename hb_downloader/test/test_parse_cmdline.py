#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
from hb_downloader.config_data import ConfigData
from hb_downloader.configuration import Configuration

actions = ["download", "download-product", "list"]

def test_help():
    # Check that the script runs and displays the help text without errors
    subprocess.check_output([sys.executable, "hb-downloader.py", "-h"])

    # Check the same with basic actions
    for a in actions:
        subprocess.check_output([sys.executable, "hb-downloader.py", a, "-h"])


def test_parse_to_config():
    """
        Checks that parameters gets parsed correctly to config
    """
    test_platforms = Configuration.cmdline_platform.copy()
    test_platforms.pop('all', None)
    for action in ["download", "list"]:
        # testing 'all'
        sys.argv = ["", action, 'all']
        Configuration.load_configuration("hb-downloader-settings.yaml")
        Configuration.parse_command_line()
        for platform in Configuration.cmdline_platform['all']:
            print("checking if %s is enabled when 'all' is specified" % platform)
            assert(ConfigData.download_platforms.get(platform) is True)

        # testing specific platforms except 'all'
        for platform in test_platforms:
            sys.argv = ["", action, platform]
            Configuration.load_configuration("hb-downloader-settings.yaml")
            Configuration.parse_command_line()
            for platform_all in test_platforms:
                # iterate even on non selected platforms
                for hb_platform in Configuration.cmdline_platform.get(
                        platform_all):
                    print("evaluating %s of %s while %s %s was selected" % (
                            hb_platform, platform_all, action, platform))
                    status = ConfigData.download_platforms.get(hb_platform)
                    # Every platform we selected must be activated
                    if platform_all == platform and status is not True:
                        print(("%s is not set to True while it should have "
                               "been for %s %s") %
                              (hb_platform, action, platform))
                        assert(False)
                    if platform_all != platform and status is not False:
                        print(("%s is not set to False while it should have "
                               "been for %s %s") %
                              (hb_platform, action, platform))
                        assert(False)


def test_single_download_to_config():
    """
        Tests downloading a single product by product key
    """
    sys.argv = ["", "download-product", "ABCdeFGhIjKL"]
    Configuration.load_configuration("hb-downloader-settings.yaml")
    Configuration.parse_command_line()
    assert(ConfigData.action == "download-product")
    for platform in Configuration.cmdline_platform['all']:
        print("checking if %s is enabled as it should" % platform)
        assert(ConfigData.download_platforms.get(platform) is True)
    assert(ConfigData.download_product == 'ABCdeFGhIjKL')


def test_single_url_to_config():
    """
        Tests downloading a product by product url which you'd find in your
        confirmation email
    """
    sys.argv = ["", "download-product", "https://www.humblebundle.com/?key=mNoPqRsTuVW&guard=ABCDEF"]
    Configuration.load_configuration("hb-downloader-settings.yaml")
    Configuration.parse_command_line()
    assert(ConfigData.action == "download-product")
    for platform in Configuration.cmdline_platform['all']:
        print("checking if %s is enabled as it should" % platform)
        assert(ConfigData.download_platforms.get(platform) is True)
    assert(ConfigData.download_product == 'mNoPqRsTuVW')


def test_simple_parse_to_config():
    """
        Tests a few predefined parameters, and check if they match the config
    """
    sys.argv = ["", "list", "games", "--platform", "windows", "linux"]
    Configuration.load_configuration("hb-downloader-settings.yaml")
    Configuration.parse_command_line()
    assert(ConfigData.action == "list")
    assert(ConfigData.download_platforms["linux"] is True)
    assert(ConfigData.download_platforms["windows"] is True)
    for platform in ["mac", "ebook", "audio", "asmjs"]:
        print("checking if %s is disabled as it should" % platform)
        assert(ConfigData.download_platforms.get(platform) is False)
