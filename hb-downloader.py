#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hb_downloader.logger as logger
from hb_downloader.config_data import ConfigData
from hb_downloader.configuration import Configuration
from hb_downloader.event_handler import EventHandler
from hb_downloader.humble_api.humble_api import HumbleApi
from hb_downloader.actions import Action

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2016 Brian Schkerke"
__license__ = "MIT"


print("Humble Bundle Downloader v%s" % ConfigData.VERSION)
print("This program is not affiliated nor endorsed by Humble Bundle, Inc.")
print("For any suggestion or bug report, please create an issue at:\n%s" %
      ConfigData.BUG_REPORT_URL)
print("")

# Load the configuration from the YAML file...
try:
    Configuration.load_configuration("/etc/hb_downloader.yaml")
except FileNotFoundError:
    print("Configuration File not found in /etc")
    print("Trying local instead...")
    Configuration.load_configuration("hb-downloader-settings.yaml")

Configuration.parse_command_line()
Configuration.dump_configuration()
Configuration.push_configuration()

validation_status, message = Configuration.validate_configuration()
if not validation_status:
    logger.display_message(False, "Error", message)
    exit("Invalid configuration.  Please check your command line arguments and "
         "hb-downloader-settings.yaml.")

# Initialize the event handlers.
EventHandler.initialize()

hapi = HumbleApi(ConfigData.auth_sess_cookie)

if not hapi.check_login():
        exit("Login to humblebundle.com failed."
             "  Please verify your authentication cookie")

logger.display_message(False, "Processing", "Downloading order list.")
game_keys = hapi.get_gamekeys()
logger.display_message(False, "Processing", "%s orders found." %
                       (len(game_keys)))

if ConfigData.action == "download":
    Action.batch_download(hapi, game_keys)
elif ConfigData.action == "download-product":
    if ConfigData.download_product in game_keys:
        Action.batch_download(hapi, [ConfigData.download_product])
    else:
        exit("Specified product key '" + ConfigData.download_product + "' was not found. These are the valid keys:\n" +
            ', '.join(game_keys))
else:
    Action.list_downloads(hapi, game_keys)


exit()
