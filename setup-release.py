#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#setup-release.py

'''
    #setup-release.py 
    Copyright (C) 2017 Woodcoin     Authors: Denkweise9, Lvl4Sword

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see https://www.gnu.org/licenses/.
'''

"""
py2app/py2exe build script for Electrum
Usage (Mac OS X):
     python setup.py py2app
Usage (Windows):
     python setup.py py2exe
"""
import os, re, shutil, sys
from setuptools import setup
from lib.util import print_error
from lib.version import ELECTRUM_VERSION as version
from distutils import dir_util


name = "Electrum-Woodcoin"
mainscript = 'electrum-wdc' #wdc = woodcoin,

if sys.version_info[:3] < (3, 0, 0):
    print_error("Error: " + name + " requires Python 3.0.0 or up")  #Should probably require 3.4
    sys.exit()

if sys.platform == 'darwin':
    from plistlib import Plist
    plist = Plist.fromFile('Info.plist')
    plist.update(dict(CFBundleIconFile='electrum.icns')) # Woodcoin will need it's own icons

    shutil.copy(mainscript, mainscript + '.py')
    mainscript += '.py'
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        options=dict(py2app=dict(argv_emulation=False,
                                 includes=['PyQt4.QtCore', 'PyQt4.QtGui', 'PyQt4.QtWebKit', 'PyQt4.QtNetwork', 'sip'],
                                 packages=['lib', 'gui', 'plugins', 'packages'],
                                 iconfile='electrum.icns',      # Woodcoin will need it's own icons
                                 plist=plist,
                                 resources=["icons"])),    
    )
elif ( sys.platform.startswith('win32') or  sys.platform.startswith('win64') ):
    extra_options = dict(
        setup_requires=['py2exe'],
        app=[mainscript],
    )
else:
        # Normally unix-like platforms will use "setup.py install"
        # and install the main script as such
    extra_options = dict(scripts=[mainscript])

setup(
    name=name,
    version=version,
    **extra_options
)

if sys.platform.startswith('darwin'):
    # Remove the copied py file
    os.remove(mainscript)
    resource = "dist/" + name + ".app/Contents/Resources/"

    # Try to locate qt_menu
    # Let's try the port version first!
    if os.path.isfile("/opt/local/lib/Resources/qt_menu.nib"):
        qt_menu_location = "/opt/local/lib/Resources/qt_menu.nib"
    else:
        # No dice? Then let's try the brew version
        if os.path.exists("/usr/local/Cellar"):
            qt_menu_location = os.popen("find /usr/local/Cellar -name qt_menu.nib | tail -n 1").read()
        # no brew, check /opt/local
        else:
            qt_menu_location = os.popen("find /opt/local -name qt_menu.nib | tail -n 1").read()
        qt_menu_location = re.sub('\n', '', qt_menu_location)

    if (len(qt_menu_location) == 0):
        print("Sorry couldn't find your qt_menu.nib this probably won't work")
    else:
        print("Found your qib: " + qt_menu_location)

    # Need to include a copy of qt_menu.nib
    shutil.copytree(qt_menu_location, resource + "qt_menu.nib")
    # Need to touch qt.conf to avoid loading 2 sets of Qt libraries, also needs porting to woodcoin
    fname = resource + "qt.conf"
    with file(fname, 'a'):
        os.utime(fname, None)
