#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import subprocess
from hb_downloader.config_data import ConfigData
from hb_downloader.configuration import Configuration

actions = ["download", "list"]


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
    for platform in Configuration.cmdline_platform:
        for action in actions:
            sys.argv = ["", action, platform]
            Configuration.load_configuration("hb-downloader-settings.yaml")
            Configuration.parse_command_line()
            for platform_all in Configuration.cmdline_platform:
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
