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
from urlparse import urlparse
import urllib2
import threading
import time
import subprocess
import ConfigParser
import gettext
from user import home as userhome

# <Tranlations stuff>

gettext.install(
                "gvdown",
                "po",
                unicode=True
               )

# </Translation stuff>

class fdownload(threading.Thread): # not used in this file, but by the other interfaces
    def __init__(
                 self,
                 url,
                 file
                ):

        self.file = open(
                         file,
                         'wb'
                        )
        self.url = url
        threading.Thread.__init__(self)
        self.arived_len = 0
        self.content_len = 100
        self.downloaded = lambda: 100.0*self.arived_len/int(
                                                            self.content_len
                                                           )
        self.filesize=int(
                          self.content_len
                         )/1024 # in KB

    def run(self):
        req = urllib2.Request(self.url)
        req.add_header(
                       'User-Agent',
                       '(g)vdown (http://vdown.googlecode.com)'
                      )
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
    def __init__(
                 self,
                 input,
                 filename_extension,
                 command
                ):
        threading.Thread.__init__(self)
        self.status = -1
        self.input = input
        self.filename_extension = filename_extension
        self.command = command
    def run(self):
        """
        Start converting
        """
        self.output = re.sub(
                             ".flv$",
                             self.filename_extension,
                             self.input
                            )
        final_cmd = []
        for i in self.command.split():
            final_cmd.append(
                             i.replace(
                                       "%i",
                                       self.input
                                      ).replace(
                                                "%o",
                                                self.output
                                               )
                            )
        output = subprocess.Popen(
                                  final_cmd,
                                  stdout=subprocess.PIPE
                                 ).communicate()[0]
        self.status = 0

def grep(
         pattern,
         context
        ):
    patternprog = re.compile(pattern)
    for line in context:
        a_match = patternprog.search(line)
        if (a_match):
            return line

class get_data(threading.Thread):
    """
    Fetch information
    """
    def __init__(
                 self,
                 url
                ):
        threading.Thread.__init__(self)
        self.status = -1
        self.url = url
        self.data = [
                     None, # download link
                     None, # title
                     None, # filename
                     None  # is this already converted? (e.g. as .avi)
                    ]
        self.regex = {
                      "youtube" : "(http://)?(www.)?youtube.com/watch\?v=([A-Za-z0-9-_]*)(&.*|$)"
                     }
    def run(self):
        try: # now we can do everything we want and everything is catched by this (please don't kill me for that)
            if re.match(
                        self.regex["youtube"],
                        self.url
                       ) != None:
                video_id = re.match(
                                    self.regex["youtube"],
                                    self.url
                                   ).group(3)
                SITE = urlparse(self.url)[1]
                PATH = urlparse(self.url)[2]+"?"+urlparse(self.url)[4]
                con = httplib.HTTPConnection(SITE)
                con.request(
                            "GET",
                            PATH
                           )
                resp = con.getresponse()
                lines = resp.read().split("\n")
                data_line = grep(
                                 "var swfArgs = ",
                                 lines
                                )
                if not data_line:
                    raise RuntimeError
                verification_code = re.match(
                                             '.*"t": "([^"]*)",.*',
                                             data_line
                                            ).group(1)
                title_line = grep(
                                  "<title>.*</title>",
                                  lines
                                 )
                pattern = re.compile("<title>.*</title>")
                if not title_line:
                    raise RuntimeError
                TITLE=re.match(
                               ".*<title>YouTube - (.*)</title>.*",
                               title_line
                              ).group(1)
                DOWNLOADLINK = "http://youtube.com/get_video?video_id="+video_id+"&t="+verification_code
                FILENAME = TITLE+".flv"
                self.data = [
                             DOWNLOADLINK,
                             TITLE,
                             FILENAME,
                             True
                            ]
            
            else:
                raise RuntimeError

        except: # if any error appeared in the code above, the video information could not be fetched successfully
            self.status = 1
        else:
            self.status = 0

def folder_is_writable(dir):
    """
    Check if we can write into a folder (creates a testfile there)
    """
    EXISTS = os.path.isfile( # do not delete the test file if it exists
                            os.path.join(
                                         dir,
                                         "vdown_test.testfile"
                                        )
                           )

    try:
        file = open(
                    os.path.join(
                                 dir,
                                 "vdown_test.testfile"
                                ),
                    "wb"
                   )
        file.close()
    except IOError:
        return False
    else:
        if not EXISTS:
            os.remove(
                      os.path.join(
                                   dir,
                                   "vdown_test.testfile"
                                  )
                     )
        return True

class configuration(ConfigParser.RawConfigParser):
    """
    Configuration class (based on RawConfigParser)
    """
    def __init__(self):
        ConfigParser.RawConfigParser.__init__(self)
        self.configfilename = os.path.join(
                                           userhome,
                                           ".gvdownrc"
                                          )
        if not os.path.isfile(self.configfilename):
            print _("Config file %s not found. Creating one for you..." % (self.configfilename))
            self.set_defaults()
            self.write_config()

    def readconfig(self):
        """
        Read config file and check for errors.
        If an error occurs while reading the settings (e.g. ConfigParser.NoSectionError), all settings will be set to default.
        """
        self.readfp(
                    open(
                         self.configfilename
                        )
                   )
        try:
            test = self.get(
                            "general",
                            "save_videos_in"
                           )
            test = self.getboolean(
                                   "general",
                                   "convert"
                                  )
            test = self.get(
                            "general",
                            "convertcmd"
                           )
            test = self.get(
                            "general",
                            "convert_filename_extension"
                           )
            test = self.getboolean(
                                   "general",
                                   "delete_source_file_after_converting"
                                  )
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

        self.set(
                 "general",
                 "save_videos_in",
                 os.path.join(
                              userhome,
                              "downloads"
                             )
                )
        self.set(
                 "general",
                 "convert",
                 "no"
                )
        self.set(
                 "general",
                 "convertcmd",
                 "ffmpeg -i %i -acodec mp3 -ab 128 %o"
                )
        self.set(
                 "general",
                 "convert_filename_extension",
                 ".mp3"
                )
        self.set(
                 "general",
                 "delete_source_file_after_converting",
                 "no"
                )

    def write_config(self):
        """
        Write config file
        """
        f = file(
                 self.configfilename,
                 "w"
                )
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
