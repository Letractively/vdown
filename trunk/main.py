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

import sys, httplib, re, urllib2, threading, time


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

class get_data(threading.Thread):
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
