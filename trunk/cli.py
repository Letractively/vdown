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
# Filename   : cli.py                                                      *
# Description: Downloads videos from video sharing websites like YouTube,  *
#       Myspace Video, Google Video, Clipfish and so on.                   *
# This application uses <videograb.de>                                     *
# The video will be saved as FLV file.                                     *
#***************************************************************************/

from main import fdownload
from main import convert as fconvert
from main import get_data
from main import folder_is_writable
import os, sys, time
import re
from time import sleep
import ConfigParser

to_avi_with_ffmpeg = True

try:
	if os.path.isdir(sys.argv[1]):
		save_videos_in = sys.argv[1]
	else:
		save_videos_in = "."
except IndexError:
	print "Please specify at least one parameter."
	print "Examples: "
	print sys.argv[0]+" /home/testuser/videos URL1 [URL2 ...]"
	print "or"
	print sys.argv[0]+" URL1 [URL2 ...]"
	sys.exit(1)

if not folder_is_writable(save_videos_in):
	print "Can't write to this directory! Change to another."
	sys.exit(1)

homedir = os.path.expanduser("~")
configfilename = homedir+"/.gvdownrc"
config = ConfigParser.RawConfigParser()

if not os.path.isfile(configfilename):
	config.add_section("general")
	config.set("general", "convert", "no")
	config.set("general", "convertcmd", "convertsth --input %i --output %o")
	config.set("general", "convert_filename_extension", ".avi")
	config.set("general", "delete_source_file_after_converting", "no")
	write_config()

config.readfp(open(configfilename))
try:
	convert = config.getboolean("general", "convert")
	convertcmd = config.get("general", "convertcmd")
	convert_filename_extension = config.get("general", "convert_filename_extension")
	deletesourcefile = config.getboolean("general", "delete_source_file_after_converting")
except ConfigParser.NoSectionError: # if not all settings are set, set all settings to default ;)
	config.add_section("general")
	config.set("general", "convert", "no")
	config.set("general", "convertcmd", "convertsth --input %i --output %o")
	config.set("general", "convert_filename_extension", ".avi")
	config.set("general", "delete_source_file_after_converting", "no")
	write_config()
	save_videos_in = config.get("general", "save_videos_in")
	convert = config.getboolean("general", "convert")
	convertcmd = config.get("general", "convertcmd")

	def write_config(self):
		f = file(configfilename, "w")
		config.write(f)
		f.close()

for i in sys.argv:
	if i != sys.argv[0] and i != save_videos_in:
		print "----"
		print "Trying to download the video..."
		print "URL: "+i
		try: 
			data = get_data(i)
			data.start()
			while data.status == -1:
				time.sleep(0.02)
			if data.status == 0:
				print "Saving file as \"%s\"..." % (data.data[2])
				down = fdownload(data.data[0], save_videos_in+"/"+data.data[2])
				down.start()
				progress = down.downloaded()
				last_progress = progress
				last_ETA = 0.00
				sleep(1) # give "it" some time to get the filesize, otherwise it'd be just '100'
				filesize = down.get_filesize()
				while filesize == 0: # if it was not enough
					sleep(1)
					filesize = down.get_filesize()
				print "Filesize: ",filesize,"KB"
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
					sys.stdout.write("\r%.2f \033[6G percent downloaded | %s \033[35G KB/s | ETA: %s \033[55Gseconds" % (float(progress), str(kb_per_sec_asfloat).rjust(7), ETA)) # makes it look more static
					sys.stdout.flush()
					last_progress = progress
					sleep(1)
					progress = down.downloaded()
					if(progress == 100.0):
						sys.stdout.write("\rDownload finished...                                   \n")
						if convert:
							print "Converting file"
							output = fconvert(save_videos_in+"/"+data.data[2], convert_filename_extension, convertcmd)
							output.start()
							while output.status == -1:
								sleep(0.2)
							print "Converted file."
							if deletesourcefile:
								os.remove(save_videos_in+"/"+data.data[2])
								print "Deleted input (.flv) file"
						break
			else:
				print "Could not fetch the wanted line. Wrong URL or unsupported video portal! But better try again."
		except KeyboardInterrupt:
			print "\nKilled by STRG+C, quitting..."
			sys.exit(1)
		print "----"
