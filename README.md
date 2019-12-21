# Question!

How many of use Windows vs. Linux to run this software?  I have an idea to accommodate the CAPTCHA and make the downloader more interactive, but I don't have the expertise to create it on Linux -- thus will only do it if you guys are using Windows.

Please let me know at bmschkerke@gmail.com which OS you use and if you'd be interested.

# hb-downloader
[![Coverage Status](https://coveralls.io/repos/github/MayeulC/hb-downloader/badge.svg)](https://coveralls.io/github/MayeulC/hb-downloader)
[![Build Status](https://travis-ci.org/MayeulC/hb-downloader.svg)](https://travis-ci.org/MayeulC/hb-downloader)

An automated utility to download your Humble Bundle purchases

    http://www.humblebundle.com

This package is not endorsed, supported, or affiliated with Humble Bundle, Inc.

It is distributed under the MIT license, you may use, modify and redistribute
it freely provided you agree with the terms of that license, that can be found
online or under the accompanying LICENSE file.

This is a fork with additional functionality and fixes of the software
originally distributed by Brian Schkerke and available at
https://github.com/talonius/hb-downloader

This repository contains code from Joel Pedraza's awesome humblebundle-python
library, available at https://github.com/saik0/humblebundle-python

## Requirements
* Python 3.6
* requests library
* pyyaml library

## Python Installation
Several features particular to Python v3.6 might have been used during the
development of this script.  To install Python v3.6 visit
https://www.python.org/downloads/ and grab the latest 3.x.x release.

## Getting the Prerequisites
From a command prompt, enter:

    pip install requests
    pip install pyyaml

You'll either be informed that the requirement is already satisfied, or pip
will retrieve, install, and configure the libraries for you.

## Getting the Installation Files
Perform one of the following actions:
* Download the zip file from the [releases
  page](https://github.com/MayeulC/hb-downloader/releases) and unzip it to the
  directory of your choice.
* Download the latest code from the [master
  branch](https://github.com/MayeulC/hb-downloader/archive/master.zip) as a zip
  file
* Check out the source with Git:
  `git clone git://github.com/MayeulC/hb-downloader.git`

## Installation
After getting the installation files, you then need to fetch your
authentication cookie from humblebundle.com.  To do so, navigate there, log in
and press F12 to open the developer tools of your browser. Navigate to the
cookies tab, and look for a cookie named `_simple_auth` (on the
humblebundle.com domain). Copy the value inside the
`hb-downloader-settings.yaml` file, or specify it on the command line with the
"-c" flag. Pay attention that every character is correctly escaped according to
the method you choose.

`hb-downloader-settings.yaml` is the configuration file for the script.  It
contains all of the information that can be overridden during script execution
trough the command line interface. The format (for the data we're concerned
with) is:
 
     <variable name>: <variable value>

download-location is where you want the files to be stored during and after
their download from humblebundle.com.  This location needs to exist and be
writable by the user executing the script.  It can be a Linux style directory
(`/mnt/Mila/Games/Humble Bundle`), a UNC share
(`\\megatron\mila\games\humble bundle`) or a Windows drive reference
(`C:\Users\Username\Downloads`):

    download-location:  \\megatron\mila\games\humble bundle

## Issues
If you encounter any issues or have suggestions, please [open a **NEW**
issue](https://github.com/MayeulC/hb-downloader/issues) on GitHub.

## Known Issues
If you run the script in a terminal window under Windows you may receive:

     UnicodeEncodeError: 'charmap' codec can't encode character...
     
This only happens if you have an extended character in the name of one of your
products.  The easiest fix is to export an environment variable so that Python
knows the terminal can accept Unicode:

    set PYTHONIOENCODING=UTF-8
