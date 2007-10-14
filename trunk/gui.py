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
# Filename   : gui.py                                                      *
# Description: Downloads videos from video sharing websites like YouTube,  *
#       Myspace Video, Google Video, Clipfish and so on.                   *
# This application uses <videograb.de>                                     *
# The video will be saved as FLV file.                                     *
#***************************************************************************/

import os, sys, re

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
from main import fdownload
from main import convert
from main import get_data
from main import folder_is_writable
import ConfigParser

gladefile = "gvdown.glade"

class gui:
	def __init__(self):
		self.wTree = gtk.glade.XML(gladefile)
		dic = {"closedSomehow" : self.closedSomehow,
			"download_single" : self.download_single,
			"menu_help_info_clicked" : self.menu_help_info_clicked,
			"on_aboutdialog_delete" : self.on_aboutdialog_delete,
			"menu_file_open_clicked" : self.menu_file_open_clicked,
			"fc_open_file_clicked" : self.download_list,
			"fc_cancel_clicked" : self.fc_cancel_clicked,
			"on_filechooserdialog_delete" : self.on_filechooserdialog_delete,
			"menu_file_settings_clicked" : self.menu_file_settings_clicked,
			"on_swindow_delete" : self.on_swindow_delete,
			"swindow_close_clicked" : self.swindow_close_clicked}
		self.wTree.signal_autoconnect(dic)

		self.homedir = os.path.expanduser("~")
		self.configfilename = self.homedir+"/.gvdownrc"
		self.config = ConfigParser.RawConfigParser()

		if not os.path.isfile(self.configfilename):
			self.config.add_section("general")
			self.config.set("general", "save_videos_in", self.homedir+"/downloads")
			self.config.set("general", "convert", "no")
			self.config.set("general", "convertcmd", "convertsth --input %i --output %o")
			self.config.set("general", "convert_filename_extension", ".avi")
			self.config.set("general", "delete_source_file_after_converting", "no")
			self.write_config()

		self.config.readfp(open(self.configfilename))
		try:
			self.save_videos_in = self.config.get("general", "save_videos_in")
			self.convert = self.config.getboolean("general", "convert")
			self.convertcmd = self.config.get("general", "convertcmd")
			self.convert_filename_extension = self.config.get("general", "convert_filename_extension")
			self.deletesourcefile = self.config.getboolean("general", "delete_source_file_after_converting")
		except ConfigParser.NoSectionError: # if not all settings are set, set all settings to default ;)
			self.config.add_section("general")
			self.config.set("general", "save_videos_in", self.homedir+"/downloads")
			self.config.set("general", "convert", "no")
			self.config.set("general", "convertcmd", "convertsth --input %i --output %o")
			self.config.set("general", "convert_filename_extension", ".avi")
			self.config.set("general", "delete_source_file_after_converting", "no")
			self.write_config()
			self.save_videos_in = self.config.get("general", "save_videos_in")
			self.convert = self.config.getboolean("general", "convert")
			self.convertcmd = self.config.get("general", "convertcmd")

		if not os.path.isdir(self.save_videos_in):
			try:
				os.mkdir(self.save_videos_in)
			except OSError:
				print "Could not create the directory where the videos shall be saved in (specified in ~/.gvdownrc)! Check permissions."
				sys.exit(1)
		if not folder_is_writable(self.save_videos_in):
			print "Cannot write to video output directoy! Check permissions or change the directory in ~/.gvdownrc"
			sys.exit(1)

	def write_config(self):
		f = file(self.configfilename, "w")
		self.config.write(f)
		f.close()

	def closedSomehow(self, widget, event = None):
		gtk.main_quit()

	def download_single(self, widget, event = None):
		entry_url = self.wTree.get_widget("entry_url")
		pb = self.wTree.get_widget("dprogressbar")
		mainDownload_button = self.wTree.get_widget("mainDownload_button")
		mainClose_button = self.wTree.get_widget("mainClose_button")
		url = entry_url.get_text()
		os.chdir(self.save_videos_in)
		pb.set_fraction(0)
		pb.set_text("Fetching video information...")
		if url == "":
			pb.set_text("No URL specified")
		else:
			print "----"
			print "Trying to download %s" % (url)
			pb.set_fraction(0)
			mainDownload_button.set_sensitive(False)
			mainClose_button.set_sensitive(False)
			data = get_data(url)
			data.start()
			while data.status == -1:
				gtk.main_iteration_do(False)
				sleep(0.01)
			gtk.main_iteration_do(True)
			if data.status == 0:
				print "Saving file as \"%s\"..." % (self.save_videos_in+"/"+data.data[2])
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
				if self.convert:
					pb.set_text("Converting file")
					output = convert(self.save_videos_in+"/"+data.data[2], self.convert_filename_extension, self.convertcmd)
					output.start()
					while output.status == -1:
						gtk.main_iteration_do(False)
						sleep(0.01)
					gtk.main_iteration_do(True)
					pb.set_text("Converted file.")
					if self.deletesourcefile:
						os.remove(self.save_videos_in+"/"+data.data[2])
						print "Deleted input (.flv) file"		
			else:
				pb.set_text("Wrong URL / unsupported video portal")
			mainDownload_button.set_sensitive(True)
			mainClose_button.set_sensitive(True)
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
		fc.set_current_folder(self.homedir)
		fc.show()

	def on_filechooserdialog_delete(self, widget, event):
		print "fcdelete"
		fc = self.wTree.get_widget("filechooserdialog")
		fc.hide()
		return True

	def fc_cancel_clicked(self, widget): # Clicked on button 'cancel' in filechooserdialog
		fc = self.wTree.get_widget("filechooserdialog")
		fc.hide()

	def download_list(self, widget): # Clicked on button 'open' in filechooserdialog
		fc = self.wTree.get_widget("filechooserdialog")
		pb = self.wTree.get_widget("dprogressbar")
		mainDownload_button = self.wTree.get_widget("mainDownload_button")
		mainClose_button = self.wTree.get_widget("mainClose_button")
		os.chdir(self.save_videos_in)
		fc.hide()
		pb.set_fraction(0)
		chosen_list = fc.get_filename()
		print "%s selected" % (chosen_list)
		print "-----"
		mainDownload_button.set_sensitive(False)
		mainClose_button.set_sensitive(False)
		pb.set_text("Downloading a list...")
		file = open(chosen_list, "r")
		i = 0
		successful = 0 # videos downloaded successfully
		while True:
			pb.set_fraction(0)
			pb.set_text("Fetching video information...")
			line = file.readline()
			if not line:
				break
			if line[-1] == "\n":
				line = line[:-1]
			print "----"
			print "Trying to download %s" % (line)
			data = get_data(line)
			data.start()
			while data.status == -1:
				gtk.main_iteration_do(False)
				sleep(0.01)
			gtk.main_iteration_do(True)
			if data.status == 0:
				print "Saving file as \"%s\"..." % (self.save_videos_in+"/"+data.data[2])
				down = fdownload(data.data[0], data.data[2])  # (http://*.*/*, *.flv)
				down.start()
				pb.set_text("Downloading video #%s" % (i+1))
				progress = down.downloaded()/100
				while down.get_filesize() == 0:
					gtk.main_iteration_do(False)
					sleep(0.01)
				gtk.main_iteration_do(True)
				filesize = down.get_filesize()
				print "Filesize: %s KB" % (filesize)
				while progress < 1:
					gtk.main_iteration_do(False)
					sleep(0.005)
					pb.set_fraction(progress)
					progress = down.downloaded()/100
				gtk.main_iteration_do(True)				
				pb.set_fraction(1)
				pb.set_text("Finished download #%s" % (i+1))
				successful += 1
				if self.convert:
					pb.set_text("Converting file")
					output = convert(self.save_videos_in+"/"+data.data[2], self.convert_filename_extension, self.convertcmd)
					output.start()
					while output.status == -1:
						gtk.main_iteration_do(False)
						sleep(0.01)
					gtk.main_iteration_do(True)
					pb.set_text("Converted file.")
					if self.deletesourcefile:
						os.remove(self.save_videos_in+"/"+data.data[2])
						print "Deleted input (.flv) file"
			else:
				print "Wrong URL / unsupported video portal"
				pb.set_text("Download #%s failed" % (i+1))
			i += 1
			print "----"
		pb.set_text("%s of %s successful" % (successful, i))
		mainDownload_button.set_sensitive(True)
		mainClose_button.set_sensitive(True)
		print "-----"

##

	def menu_file_settings_clicked(self, widget):
		swindow = self.wTree.get_widget("settingswindow")
		sfcb = self.wTree.get_widget("sfcb") # settings filechooser button
		convertbutton = self.wTree.get_widget("convertbutton")
		convertcmdentry = self.wTree.get_widget("convertcmdentry")
		deletesourcefilebutton = self.wTree.get_widget("deletesourcefilebutton")
		sfcb.set_local_only(True)
		sfcb.set_show_hidden(False)
		sfcb.set_current_folder(self.save_videos_in)
		convertbutton.set_active(self.convert)
		convertcmdentry.set_text(self.convertcmd)
		deletesourcefilebutton.set_active(self.deletesourcefile)
		swindow.show()

	def on_swindow_delete(self, widget, event):
		swindow = self.wTree.get_widget("settingswindow")
		swindow.hide()
		return True

	def swindow_close_clicked(self, widget):
		sfcb = self.wTree.get_widget("sfcb")
		swindow = self.wTree.get_widget("settingswindow")
		convertcmdentry = self.wTree.get_widget("convertcmdentry")
		convertbutton = self.wTree.get_widget("convertbutton")
		deletesourcefilebutton = self.wTree.get_widget("deletesourcefilebutton")
		outputdir = sfcb.get_filename()
		if convertbutton.get_active():
			self.convert = True
			self.config.set("general", "convert", "yes")
		else:
			self.convert = False
			self.config.set("general", "convert", "no")
		self.convertcmd = convertcmdentry.get_text()
		self.config.set("general", "convertcmd", self.convertcmd)
		self.deletesourcefile = deletesourcefilebutton.get_active()
		if self.deletesourcefile:
			self.config.set("general", "delete_source_file_after_converting", "yes")
		else:
			self.config.set("general", "delete_source_file_after_converting", "no")
		self.write_config()
		if not folder_is_writable(self.save_videos_in):
			print "Cannot write to video output folder. Choose another."
		else:
			self.config.set("general", "save_videos_in", outputdir)
			self.save_videos_in = outputdir
			self.write_config()
			swindow.hide()

##

if __name__ == "__main__":
	try:
		fileread = open(gladefile)
		fileread.close()
	except:
		print "Could not open \"" + gladefile + "\"."
		sys.exit(1)

app = gui()
gtk.main()
