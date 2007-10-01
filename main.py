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
# The video will be saved as FLV file in your home directory.              *
#***************************************************************************/

import sys, httplib, re
def get_data(url):
	SITE="www.videograb.de"
	FILENAME="/cgi-bin/video.cgi?url="+url

	con_vg=httplib.HTTPConnection(SITE)
	con_vg.request("GET", FILENAME)
	con_vg_info = con_vg.getresponse()
	con_vg_data=con_vg_info.read()

	try:
		WANTEDLINE=[ l for l in con_vg_data.splitlines() if ">Download von " in l][0] # echo "rabfoo \nfoobar" | grep bar
	except IndexError:
		print "Could not grep the wanted line! Wrong URL or unsupported video portal!"
		raise sys.exit(1)
	else:
		WANTEDLINK=re.sub(">Download$", "", re.sub("\"", "", re.sub("href\=", "", re.split(" ", WANTEDLINE)[1])))
		WANTEDNAME=re.sub("<br>$", "", re.split("</a>: ", WANTEDLINE)[1])
		VIDEO_FILENAME=re.sub("(?i).flv.flv", ".flv", WANTEDNAME+".flv")
		return [WANTEDLINK, WANTEDNAME, VIDEO_FILENAME]

if __name__ == "__main__":
	for i in sys.argv:
		if i != sys.argv[0]:
			print "----"
			print "URL           : "+i
			try:
				data = get_data(i)
				print "Download link : "+data[0]
				print "Video name: "+data[1]
			except:
				print "Could not get infos, trying next URL (if any)..."
