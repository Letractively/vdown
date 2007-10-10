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
from main import get_data
from download import fdownload

gladefile = "gvdown.glade"

class gui:
	def __init__(self):
		self.wTree = gtk.glade.XML(gladefile)
		dic = {"closedSomehow" : self.closedSomehow,
			"download_single" : self.download_single}
		self.wTree.signal_autoconnect(dic)
		self.wTree.get_widget("dprogressbar").set_text("Nothing to do")

	def closedSomehow(self, widget, event = None):
		gtk.main_quit()

	def download_single(self, widget, event = None):
		entry_url = self.wTree.get_widget("entry_url")
		pb = self.wTree.get_widget("dprogressbar")
		url = entry_url.get_text()
		if url == "":
			dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
							message_format = "No URL specified!",
							buttons=gtk.BUTTONS_OK)
			dialog.set_title("No URL")
			dialog.run()
			dialog.destroy()
		else:
			pb.set_text("Fetching video information...")
			print "Trying to download %s" % (url)
			data = get_data(url)
			print "Saving file as \"%s\"..." % (data[2])
			down = fdownload(data[0], data[2])
			down.start()
			pb.set_text("Downloading video...")
			progress = down.downloaded()/100
			while down.get_filesize() == 0:
				gtk.main_iteration_do(False)
			gtk.main_iteration_do(True)
			filesize = down.get_filesize()
			print "Filesize: %s KB" % (filesize)
			while progress < 1:
				gtk.main_iteration_do(False)
				pb.set_fraction(progress)
				progress = down.downloaded()/100
			gtk.main_iteration_do(True)
			pb.set_text("Download finished.")
		
if __name__ == "__main__":
	try:
		fileread = open(gladefile)
		fileread.close()
	except:
		print "Could not open \"" + gladefile + "\"."
		sys.exit(1)

app = gui()
gtk.main()
