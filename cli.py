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
# The video will be saved as FLV file in your home directory.              *
#***************************************************************************/

from main import get_data
import sys, time
import download
import re
from time import sleep

for i in sys.argv:
	if i != sys.argv[0]:
		print "---"
		print "Trying to download the video..."
		print "URL: "+i
		try: 
			data = get_data(i)
			print "Saving file as \"%s\"..." % (data[2])
			down = download.fdownload(data[0], data[2])
			down.start()
			progress = down.downloaded()
			last_progress = progress
			sleep(1) # give "it" some time to get the filesize, otherwise it'd be just '100'
			filesize = down.get_filesize()
			print "Filesize: ",filesize,"KB"
			while True:
				progress_dif = progress-last_progress
				kb_per_sec = filesize*(progress_dif/1000)
				progress_2dec = round(progress, 2) # only 2 decimal places!
				downloaded_kb = (progress_2dec/100)*filesize
				if kb_per_sec < 1:
					ETA = "?"
				else:
					left_kb = filesize-downloaded_kb
					ETA = round(left_kb/kb_per_sec, 2)
				sys.stdout.write("\r%s percent downloaded | %s KB/s | ETA: %ss  " % (progress_2dec, (round(kb_per_sec, 2)), ETA))
				sys.stdout.flush()
				time.sleep(1)
				progress = down.downloaded()
				if(progress == 100.0):
					sys.stdout.write("\rDownload finished! Trying next (if any)...\n")
					sys.stdout.flush()
					break
		except KeyboardInterrupt:
			print "\nKilled by STRG+C, quitting..."
			sys.exit(1)
		print "---"
			
#		except:
#			print "An error has occurred. Trying next (if any)..."
