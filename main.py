#!/usr/bin/env python
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
# Filename   : main.py                                                     *
# Description: Downloads videos from video sharing websites like YouTube,  *
#       Myspace Video, Google Video, Clipfish and so on.                   *
# This application uses <videograb.de>                                     *
# The video will be saved as FLV file.                                     *
#***************************************************************************/

import os
import sys
import httplib
import re
import urllib2
import threading
import time
import subprocess
import ConfigParser
import gettext

# <Tranlations stuff>

gettext.install("gvdown", "./po", unicode=True)

# </Translation stuff>

class fdownload(threading.Thread): # not used in this file, but by the other interfaces
    def __init__(self, url, file):
        self.file = open(file,'wb')
        self.url = url
        threading.Thread.__init__(self)
        self.arived_len = 0
        self.content_len = 100
        self.downloaded = lambda: 100.0*self.arived_len/int(self.content_len)
        self.filesize=int(self.content_len)/1024 # in KB

    def run(self):
        req = urllib2.Request(self.url)
        req.add_header('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.6) Gecko/20061201 Firefox/2.0.0.6 (Ubuntu-feisty)')
        con = urllib2.urlopen(req)
        self.content_len = con.info()['Content-length']
        arived_len = 0
        for chunk in con:
            self.arived_len += len(chunk)
            self.file.write(chunk)
        self.file.close()
    def get_filesize(self):
        return int(self.content_len)/1024

class convert(threading.Thread):
    """
    Convert video files with user-specified command
    """
    def __init__(self, input, filename_extension, command):
        threading.Thread.__init__(self)
        self.status = -1
        self.input = input
        self.filename_extension = filename_extension
        self.command = command
    def run(self):
        self.output = re.sub(".flv$", self.filename_extension, self.input)
        final_cmd = []
        for i in self.command.split():
            final_cmd.append(i.replace("%i", self.input).replace("%o", self.output))
        output = subprocess.Popen(final_cmd, stdout=subprocess.PIPE).communicate()[0]
        self.status = 0


class get_data(threading.Thread):
    """
    Fetch data from videograb.de
    """
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.status = -1
        self.url = url
        self.data = [None, None, None]
    def run(self):
        SITE="www.videograb.de"
        FILENAME="/cgi-bin/video.cgi?url="+self.url

        con_vg=httplib.HTTPConnection(SITE)
        con_vg.request("GET", FILENAME)
        con_vg_info = con_vg.getresponse()
        con_vg_data=con_vg_info.read()

        try:
            WANTEDLINE=[ l for l in con_vg_data.splitlines() if ">Download von " in l][0] # echo "rabfoo \nfoobar" | grep bar
        except IndexError:
            self.status = 1
        else:
            WANTEDLINK=re.sub(">Download$", "", re.sub("\"", "", re.sub("href\=", "", re.split(" ", WANTEDLINE)[1])))
            WANTEDNAME=re.sub("<br>$", "", re.split("</a>: ", WANTEDLINE)[1])
            VIDEO_FILENAME=re.sub("(?i).flv.flv", ".flv", WANTEDNAME+".flv")
            self.status = 0
            self.data = [WANTEDLINK, WANTEDNAME, VIDEO_FILENAME]

def folder_is_writable(dir):
    """
    Check if we can write into a folder (creates a testfile there)
    """
    if os.path.isfile(dir+"/vdown_test.testfile"): # do not delete the test file if it exists
        EXISTS = True
    else:
        EXISTS = False

    try:
        file = open(dir+"/vdown_test.testfile", "wb")
        file.close()
    except IOError:
        return False
    else:
        if not EXISTS:
            os.remove(dir+"/vdown_test.testfile")
        return True

class configuration(ConfigParser.RawConfigParser):
    """
    Configuration class (based on RawConfigParser)
    If an error occurs while reading the settings (e.g. ConfigParser.NoSectionError), all settings will be set to default.
    """
    def __init__(self):
        ConfigParser.RawConfigParser.__init__(self)
        self.configfilename = os.path.expanduser("~")+"/.gvdownrc"
        if not os.path.isfile(self.configfilename):
            print _("Config file %s not found. Creating one for you..." % (self.configfilename))
            self.set_defaults()
            self.write_config()

    def readconfig(self):
        self.readfp(open(self.configfilename))
        try:
            test = self.get("general", "save_videos_in")
            test = self.getboolean("general", "convert")
            test = self.get("general", "convertcmd")
            test = self.get("general", "convert_filename_extension")
            test = self.getboolean("general", "delete_source_file_after_converting")
        except:
            self.set_defaults()
            self.write_config()

    def set_defaults(self):
        print _("Setting settings to default...")
        if not self.has_section("general"):
            self.add_section("general")
        self.set("general", "save_videos_in", os.path.expanduser("~/downloads"))
        self.set("general", "convert", "no")
        self.set("general", "convertcmd", "convertsth --input %i --output %o")
        self.set("general", "convert_filename_extension", ".avi")
        self.set("general", "delete_source_file_after_converting", "no")

    def write_config(self):
        f = file(self.configfilename, "w")
        self.write(f)
        f.close()

if __name__ == "__main__":
    for i in sys.argv:
        if i != sys.argv[0]:
            print "----"
            print "URL           : "+i

            data = get_data(i)
            data.start()
            while data.status == -1:
                time.sleep(0.02)
            if data.status == 0:
                print "Download link : "+data.data[0]
                print "Video name    : "+data.data[1]
            else:
                print "Could not fetch the wanted line. Wrong URL or unsupported video portal!"
            print "----"
