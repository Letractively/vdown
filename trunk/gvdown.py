#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys, os
from time import sleep

try:
	import pygtk
	pygtk.require("2.0")
except:
	print "PyGTKv2 needed."
	sys.exit(1)

try:
	import gtk
	import gtk.glade
except:
	print "GTKv2 needed."
	sys.exit(1)
try:
	from subprocess import Popen
except:
	print "Subprocess module needed!"
	sys.exit(1)

class gui:
	def __init__(self):
		self.vdown_path = "/usr/bin/vdown"
		self.gladefile = "vdown.glade"
		self.wTree = gtk.glade.XML(self.gladefile)
		dic = {"download_button_clicked" : self.download_button_clicked,
				"closedSomehow" : gtk.main_quit,
				"info_clicked" : self.info_clicked,
				"on_aboutdialog_delete" : self.on_aboutdialog_delete,
				"open_pressed" : self.open_pressed,
				"on_filechooserdialog1_delete" : self.on_chooser_delete}
		self.wTree.signal_autoconnect(dic)

		self.window = self.wTree.get_widget("window")
		self.window.activate_default()
		self.download_button = self.wTree.get_widget("download_button")
		self.download_button.set_flags(gtk.CAN_DEFAULT)
		self.window.set_default(self.download_button)
		self.entry = self.wTree.get_widget("entry1")
		self.entry.set_activates_default(True)
		self.aboutdialog = self.wTree.get_widget("aboutdialog")
		self.filechooser = self.wTree.get_widget("filechooserdialog1")
	def main(self):
		gtk.main()
	def download_button_clicked(self, arg2):
		self.entry_content = self.entry.get_text()
		self.vdown_command = self.vdown_path," ",self.entry_content
		if os.path.isfile("/tmp/vdown.last"):
			os.remove("/tmp/vdown.last")
		try:
			process = Popen(self.vdown_command)
			process.wait()
		except:
			print "Error while executing ", self.vdown_command
			print "Error: ", sys.exc_info()
		if os.path.isfile("/tmp/vdown.last"):
			file = open("/tmp/vdown.last", "r") # File content = video file
			savedAs = file.read()
			file.close()
			dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO, 
							message_format="Downloaded video successfully. It was saved as \""+savedAs+"\"",
							buttons=gtk.BUTTONS_OK)
			dialog.set_title("Downloaded video.")
			dialog.run()
			dialog.destroy()
			self.returnToWindow()
		else: # Could not download video
			dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR, 
							message_format="The video could not be downloaded. This may be because the link was broken or the video portal is not supported (yet)\n"+"You entered: \""+self.entry_content+"\"", 
							buttons=gtk.BUTTONS_OK)
			dialog.set_title("Could not download video")
			dialog.run()
			dialog.destroy()
			self.returnToWindow()
	def returnToWindow(self, arg2 = None):
			self.entry.set_text("")
			self.entry.grab_focus()
	def info_clicked(self, arg2, arg3):
		self.aboutdialog.show()
	def on_aboutdialog_delete(self, arg2, arg3 = None):
		self.aboutdialog.hide()
	def open_pressed(self, arg2, arg3 = None):
		self.filechooser.set_current_folder(os.path.expanduser("~"))
		self.filechooser.set_default_response(gtk.RESPONSE_OK)
		self.chooser_response = self.filechooser.run()
		if self.chooser_response == gtk.RESPONSE_OK:
			print self.filechooser.get_filename(), 'selected'
		else:
			print 'No file selected.'
		self.filechooser.hide()
#		self.returnToWindow()
	def on_chooser_delete(self, arg2, arg3 = None):
		self.filechooser.hide()
if __name__ == "__main__":
   	if len(sys.argv) >= 2:
		if sys.argv[1] in ("-h", "--help"):
		  	print "This is a GTK user interface to download videos with vdown."
	 		print "Usage: Just execute "+sys.argv[0]+" without parameters."
			sys.exit(0)
		else:
			try:
				fileread = open(gladefile)
				fileread.close()
			except:
				print "File "+gladefile+" could not be opened!"
				sys.exit(1)
gui = gui()
gui.main()
