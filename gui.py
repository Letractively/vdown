#!/usr/bin/env python

import sys

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
import main

gladefile = "gvdown.glade"

class gui:
	def __init__(self):
		self.wTree = gtk.glade.XML(gladefile)
		dic = {"closedSomehow" : self.closedSomehow,
			"download_single" : self.download_single}
		self.wTree.signal_autoconnect(dic)

	def closedSomehow(self, widget, event = None):
		gtk.main_quit()

	def download_single(self, widget, event = None):
		entry_url = self.wTree.get_widget("entry_url")
		url = entry_url.get_text()
		if url == "":
			sleep(3)
			dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
							message_format = "No URL specified!",
							buttons=gtk.BUTTONS_OK)
			dialog.set_title("No URL")
			dialog.run()
			dialog.destroy()
		else:
			print "URL: %s" % (url)
		
		

if __name__ == "__main__":
	try:
		fileread = open(gladefile)
		fileread.close()
	except:
		print "Could not open \"" + gladefile + "\"."
		sys.exit(1)

app = gui()
gtk.main()
