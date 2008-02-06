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

import os
import sys
import httplib
import re
from urllib import urlencode
import urllib2
import threading
import time
import subprocess
import ConfigParser
import gettext
from user import home as userhome

# <Tranlations stuff>

gettext.install("gvdown", "po", unicode=True)

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
        req.add_header('User-Agent', '(g)vdown (http://vdown.googlecode.com)')
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
        """
        Start converting
        """
        self.output = re.sub(".flv$", self.filename_extension, self.input)
        final_cmd = []
        for i in self.command.split():
            final_cmd.append(i.replace("%i", self.input).replace("%o", self.output))
        output = subprocess.Popen(final_cmd, stdout=subprocess.PIPE).communicate()[0]
        self.status = 0


class get_data(threading.Thread):
    """
    Fetch data from nachrichtenmann.de/cgi-bin/video/video.cgi
    FIXME: make this a bit prettier
    """
    def __init__(self, url):
        threading.Thread.__init__(self)
        self.status = -1
        self.url = url.replace("www.stage6.com", "stage6.divx.com").replace("stage6.com", "stage6.divx.com")
        self.data = [None, None, None, None]
    def run(self):
        if re.match("(http://)?stage6.divx.com/.*/video/[0-9]*/.*", self.url) != None: # if stage6 video
            matchMe = re.match("(http://)?stage6.divx.com/.*/video/([0-9]*)/(.*)", self.url)
            video_id = matchMe.group(2)
            WANTEDLINK="http://video.stage6.com/%s/.divx" % (video_id)
            VIDEO_FILENAME=re.sub("$", ".divx", matchMe.group(3)) # add .divx at the end
            self.status = 0
            self.data = [WANTEDLINK, video_id, VIDEO_FILENAME, False]

        else:
            SITE="www.2video.de"
            FILENAME="/"
            params = urlencode({"dl" : self.url,
                                "req" : "downloads",
                                "action" : "download"})
            headers = {"Content-type": "application/x-www-form-urlencoded",
                        "Accept": "text/plain"}
            con=httplib.HTTPConnection(SITE)
            con.request("POST", FILENAME, params, headers)
            con_info=con.getresponse()
            con_data=con_info.read()
            lines=con_data.splitlines()
            SITE=re.match("(http://)?(.*)/(.*)", self.url).group(2)
            FILENAME=re.match("(http://)?(.*)/(.*)", self.url).group(3)
            con2=httplib.HTTPConnection(SITE)
            con2.request("GET", "/"+FILENAME)
            con2_data=con2.getresponse().read()
            mylines=con2_data.splitlines()

            try:
                LINKLINE_NR=lines.index([x for x in lines if 'target="_blank">Download von ' in x][0])
                WANTEDLINK=re.match('.*<a href="(.*)" target=.*', lines[LINKLINE_NR]).group(1)
                WANTEDNAME_NR=mylines.index([x for x in mylines if '<title>' in x][0])
                WANTEDNAME=re.match('.*<title>(.*)</title>.*', mylines[WANTEDNAME_NR]).group(1)
                print WANTEDNAME

            except:
                self.status = 1
            else:
                VIDEO_FILENAME=re.sub("(?i).flv.flv", ".flv", WANTEDNAME+".flv")
                self.status = 0
                self.data = [WANTEDLINK, WANTEDNAME, VIDEO_FILENAME, True]

def folder_is_writable(dir):
    """
    Check if we can write into a folder (creates a testfile there)
    """
    if os.path.isfile(os.path.join(dir, "vdown_test.testfile")): # do not delete the test file if it exists
        EXISTS = True
    else:
        EXISTS = False

    try:
        file = open(os.path.join(dir, "vdown_test.testfile"), "wb")
        file.close()
    except IOError:
        return False
    else:
        if not EXISTS:
            os.remove(os.path.join(dir, "vdown_test.testfile"))
        return True

class configuration(ConfigParser.RawConfigParser):
    """
    Configuration class (based on RawConfigParser)
    """
    def __init__(self):
        ConfigParser.RawConfigParser.__init__(self)
        self.configfilename = os.path.join(userhome, ".gvdownrc")
        if not os.path.isfile(self.configfilename):
            print _("Config file %s not found. Creating one for you..." % (self.configfilename))
            self.set_defaults()
            self.write_config()

    def readconfig(self):
        """
        If an error occurs while reading the settings (e.g. ConfigParser.NoSectionError), all settings will be set to default.
        """
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
        """
        Set settings to defaults
        """
        print _("Setting settings to default...")
        if not self.has_section("general"):
            self.add_section("general")
        self.set("general", "save_videos_in", os.path.join(userhome, "downloads"))
        self.set("general", "convert", "no")
        self.set("general", "convertcmd", "ffmpeg -i %i -acodec mp3 %o")
        self.set("general", "convert_filename_extension", ".avi")
        self.set("general", "delete_source_file_after_converting", "no")

    def write_config(self):
        """
        Write config file
        """
        f = file(self.configfilename, "w")
        self.write(f)
        f.close()

if __name__ == "__main__":
    for i in sys.argv:
        if i != sys.argv[0]:
            print "----"
            print "URL           : %(url)s" % {"url" : i}

            data = get_data(i)
            data.start()
            while data.status == -1:
                time.sleep(0.02)
            if data.status == 0:
                print _("Download link : %(dlink)s") % {"dlink" : data.data[0]}
                print _("Video name    : %(vname)s") % {"vname" : data.data[1]}
            else:
                print _("Could not fetch the wanted line. Wrong URL or unsupported video portal!")
            print "----"

