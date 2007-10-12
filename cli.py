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

from main import get_data
import sys, time
import download
import re
from time import sleep

for i in sys.argv:
	if i != sys.argv[0]:
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
				down = download.fdownload(data.data[0], data.data[2])
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
						sys.stdout.write("\rDownload finished! Trying next (if any)...                      \n")
						break
			else:
				print "Could not fetch the wanted line. Wrong URL or unsupported video portal!"
		except KeyboardInterrupt:
			print "\nKilled by STRG+C, quitting..."
			sys.exit(1)
		print "----"
