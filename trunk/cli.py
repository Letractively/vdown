#!/usr/bin/env python2.5
# -*- coding: UTF-8 -*-

#***************************************************************************\
#*   Copyright (C) 2007 by Nicolai Spohrer,                                *
#*   nicolai@xeve.de                                                       *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, see                                  *
#*   <http://www.gnu.org/licenses/gpl.html> or write to the                *
#*   Free Software Foundation, Inc.,                                       *
#*   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#***************************************************************************
# Filename   : gui.py                                                      *
# Description: Downloads videos from video sharing websites like YouTube,  *
#       Myspace Video, Google Video, Clipfish and so on.                   *
# The video will be saved as FLV file (but can be converted).              *
#***************************************************************************/

from main import fdownload
from main import convert as fconvert
from main import get_data
from main import folder_is_writable
from main import configuration
import os, sys, time
import re
from time import sleep
import gettext
from user import home as userhome
from optparse import OptionParser

# <Tranlations stuff>

gettext.install("gvdown", "po", unicode=True)

# </Translation stuff>

parser = OptionParser(usage=_("Usage: %prog [options] URL1 [URL2] [...]"))

parser.remove_option("-h")
parser.add_option("-h", "--help", action="help", help=_("show this help message and exit"))

parser.add_option("-d", "--destination", dest="destination",
                  help=_("save videos in DEST"), metavar="DEST", default=".")

parser.add_option("-s", "--save-as", dest="saveAs", help=_("save video file as FILE"), metavar="FILE", default=None)

(options, args) = parser.parse_args()

if not folder_is_writable(options.destination):
    print _("Can't write to this directory! Change to another.")
    sys.exit(1)

config = configuration()
config.readconfig()

if len(args) < 1:
    print _("Specify at least one video.")
    sys.exit(1)

for i in args:

    print "----"
    print _("Trying to download the video...")
    print _("URL: %(url)s") % {"url" : i}
    try:
        data = get_data(i)
        data.start()
        while data.status == -1:
            sleep(0.02)
        if data.status == 0:
            if options.saveAs != None:
                saveAs = options.saveAs
            else:
                saveAs = os.path.join(options.destination, data.data[2])
            print _('Saving file as "%(file)s"...') % {"file" : saveAs}
            down = fdownload(data.data[0], saveAs)
            down.start()
            progress = down.downloaded()
            last_progress = progress
            last_ETA = 0.00
            putWinString = False
            sleep(1) # give "it" some time to get the filesize, otherwise it'd be just '100'
            filesize = down.get_filesize()
            while filesize == 0: # if it was not enough
                sleep(1)
                filesize = down.get_filesize()
            print _("Filesize: %(filesize)s KB") % {"filesize" : filesize}
            while True:
                progress_dif = progress-last_progress
                kb_per_sec = filesize*(progress_dif/100)
                downloaded_kb = (progress/100)*filesize
                left_kb = filesize-downloaded_kb
                kb_per_sec_asfloat = "%.2f" % (float(kb_per_sec))
                if kb_per_sec < 1:
                    if last_ETA == 0.00:
                        ETA = "?"
                else:
                    ETA = "%.2f" % (left_kb/kb_per_sec) # may be inexact!
                    last_ETA = ETA # if kb_per_sec is 0 and something was already downloaded, print the last ETA
                seconds_string = _("seconds") # gettext + this one line under me...
                if sys.platform == "linux2":
                    sys.stdout.write("\r%.2f \033[6G %% | %s \033[18G KB/s | ETA: %s \033[38G%s" % (float(progress), str(kb_per_sec_asfloat).rjust(7), ETA, seconds_string)) # makes it look more static
                    sys.stdout.flush()
                    last_progress = progress
                    sleep(1)
                progress = down.downloaded()
                if sys.platform != "linux2" and putWinString == False:
                    print _("Downloading...")
                    putWinString = True
                if(progress == 100.0):
                    sys.stdout.write(_("\rDownload finished...                                                        \n"))
                    if config.getboolean("general", "convert") and data.data[3]:
                        print _("Converting file...")
                        output = fconvert(saveAs, config.get("general", "convert_filename_extension"), config.get("general", "convertcmd"))
                        output.start()
                        while output.status == -1:
                            sleep(0.2)
                        print _("Converted file.")
                        if config.getboolean("general", "delete_source_file_after_converting"):
                            os.remove(saveAs)
                            print _("Deleted input (.flv) file")
                    break
        else:
            print _("Could not fetch the wanted line. Wrong URL or unsupported video portal! But better try again.")
    except KeyboardInterrupt:
        print _("\nKilled by CTRL+C, quitting...")
        sys.exit(1)
    print "----"
