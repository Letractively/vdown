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
# Filename   : download.py                                                 *
# Description: Downloads videos from video sharing websites like YouTube,  *
#       Myspace Video, Google Video, Clipfish and so on.                   *
# This application uses <videograb.de>                                     *
# The video will be saved as FLV file in your home directory.              *
#***************************************************************************/

import urllib2
import threading
import time


class fdownload(threading.Thread):
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

