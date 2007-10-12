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
# Filename   : mgui.py                                                     *
# Description: Downloads videos from video sharing websites like YouTube,  *
#       Myspace Video, Google Video, Clipfish and so on.                   *
# This application uses <videograb.de>                                     *
# The video will be saved as FLV file.                                     *
#***************************************************************************/

import os, sys

try:
	import pygtk
	pygtk.require("2.0")
except:
	print "PyGTKv2 needed"
	sys.exit(1)

try:
	import gtk
	import gtk.glade
except:
	sys.exit(1)

from time import sleep
from main import get_data
from main import fdownload

gladefile = "gvdown.glade"

class gui:
	def __init__(self):
		self.wTree = gtk.glade.XML(gladefile)
		dic = {"closedSomehow" : self.closedSomehow,
			"download_single" : self.download_single,
			"menu_help_info_clicked" : self.menu_help_info_clicked,
			"on_aboutdialog_delete" : self.on_aboutdialog_delete,
			"menu_file_open_clicked" : self.menu_file_open_clicked}
		self.wTree.signal_autoconnect(dic)
		self.wTree.get_widget("dprogressbar").set_text("Nothing to do")

	def closedSomehow(self, widget, event = None):
		gtk.main_quit()

	def download_single(self, widget, event = None):
		entry_url = self.wTree.get_widget("entry_url")
		pb = self.wTree.get_widget("dprogressbar")
		url = entry_url.get_text()
		pb.set_fraction(0)
		pb.set_text("Fetching video information...")
		if url == "":
			pb.set_text("No URL specified")
		else:
			print "----"
			print "Trying to download %s" % (url)
			pb.set_fraction(0)
			data = get_data(url)
			data.start()
			while data.status == -1:
				gtk.main_iteration_do(False)
				sleep(0.01)
			gtk.main_iteration_do(True)
			if data.status == 0:
				print "Saving file as \"%s\"..." % (data.data[2])
				down = fdownload(data.data[0], data.data[2])
				down.start()
				pb.set_fraction(0)
				pb.set_text("Downloading video...")
				progress = down.downloaded()/100
				while down.get_filesize() == 0:
					gtk.main_iteration_do(False)
					sleep(0.01)
				gtk.main_iteration_do(True)
				filesize = down.get_filesize()
				print "Filesize: %s KB" % (filesize)
				while progress < 1:
					gtk.main_iteration_do(False)
					sleep(0.01)
					pb.set_fraction(progress)
					progress = down.downloaded()/100
				gtk.main_iteration_do(True)				
				pb.set_fraction(1)
				pb.set_text("Download finished.")
			else:
				pb.set_text("Wrong URL / unsupported video portal")
			print "----"

##
	def menu_help_info_clicked(self, widget, event = None):
		aboutdialog = self.wTree.get_widget("aboutdialog")
		aboutdialog.show()

	def on_aboutdialog_delete(self, widget, event):
		aboutdialog = self.wTree.get_widget("aboutdialog")
		aboutdialog.hide()
		return True
##

	def menu_file_open_clicked(self, widget):
		fc = self.wTree.get_widget("filechooserdialog")
		fc.set_current_folder(os.path.expanduser("~"))
		fc.show()

	def fc_open_file_clicked(self, widget): # Clicked on button 'open' in filechooserdialog
		print "doesnt do anything yet"

if __name__ == "__main__":
	try:
		fileread = open(gladefile)
		fileread.close()
	except:
		print "Could not open \"" + gladefile + "\"."
		sys.exit(1)

app = gui()
gtk.main()
