#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import hb_downloader.logger as logger
from hb_downloader.config_data import ConfigData
from hb_downloader.configuration import Configuration
from hb_downloader.event_handler import EventHandler
from hb_downloader.humble_api.humble_api import HumbleApi
from hb_downloader.actions import Action

__author__ = "Brian Schkerke"
__copyright__ = "Copyright 2020 Brian Schkerke"
__license__ = "MIT"

# Actual contributors to this project:
# Real Names:  Mayeul Cantan, Claudius Coenen, Katrin Leinweber, Tobi Grimm
# GitHub Aliases:  badp, wjp, humor4fun, ectotropic, bspeice
# Please email Brian Schkerke (bmschkerke@gmail.com) with your real name if 
#      you want it listed instead of your alias.

print("Humble Bundle Downloader v%s" % ConfigData.VERSION)
print("This program is not affiliated nor endorsed by Humble Bundle, Inc.")
print("For any suggestion or bug report, please create an issue at:\n%s" %
      ConfigData.BUG_REPORT_URL)
print("")
print("This script is running from and logging to %s" % os.getcwd())
print("")

# Determine which configuration file we want to use.
user_config_filename = os.path.expanduser("~/.config/%s" % ConfigData.config_filename)
system_config_filename = "/etc/%s" % ConfigData.config_filename
local_config_filename = "%s/%s" % (os.getcwd(), ConfigData.config_filename)
final_config_filename = None

# Assignment is in reverse order of priority.  Last file to exist is the one used.
if os.path.isfile(local_config_filename):
    final_config_filename = local_config_filename
if os.path.isfile(system_config_filename):
    final_config_filename = system_config_filename
if os.path.isfile(user_config_filename):
    final_config_filename = user_config_filename

if final_config_filename is None:
    exit("No configuration file found.\nLocations searched:\nUser: %s\nSystem: %s\nLocal: %s\n" %
        (user_config_filename, system_config_filename, local_config_filename))

# Load the configuration from the YAML file...
try:
    print("Loading configuration from %s" % final_config_filename)
    Configuration.load_configuration(final_config_filename)
    print("Configuration successfully loaded from %s" % final_config_filename)
except FileNotFoundError:
    exit("Configuration file was identified but could not be read.")

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
