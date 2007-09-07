import gtk.glade
import handler
import os
from sys import exc_info
from subprocess import Popen
from time import sleep
from gobject import child_watch_add

class GUI_Handler(handler.Handler):
    def __init__(self):
        handler.Handler.__init__(self, "/etc/gvdown.conf")
        self.__file = None

    def download(self, widget):
        entry_url = self.get_widget(widget, "entry_url")
        entry_content = entry_url.get_text()
        # move most of the parts below to the __download logic
        vdown_path = self.config.get("vdown", "path")
        vdown_command = vdown_path," ",entry_content
        os.chdir(os.path.expanduser("~"))   # Change to Home Directory of the user, where the videos shall be saved 
        gtk.main_iteration_do(False)
        if os.path.isfile("/tmp/vdown.last"):
            os.remove("/tmp/vdown.last")
        try:
            process = Popen(vdown_command)
        except:
            print "Could not execute ",vdown_path,"! Check the vdown path in /etc/gvdown.conf."
            print "Error: ", exc_info()
        else:
            process.wait()
            print process.returncode
            gtk.main_iteration_do(True)
        if os.path.isfile("/tmp/vdown.last"):
            if self._debug:
                print "download successfull..."
            file = open("/tmp/vdown.last", "r") # File content = video file
            savedAs = file.read()
            file.close()
            os.remove("/tmp/vdown.last")
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                   message_format="Downloaded video successfully. It was saved as \""+savedAs+"\"",
                                   buttons=gtk.BUTTONS_OK)
            dialog.set_title("Downloaded video.")
            response = dialog.run()
            if response == -5:
                if self._debug:
                    print "download successfully. destroy window"
                dialog.destroy()
        else: # Could not download video
            if self._debug:
                print "could not download video"
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
            message_format="The video could not be downloaded. This may be because the link was broken or the video portal is not supported (yet)\n"+"You entered: \""+entry_content+"\"",
            buttons=gtk.BUTTONS_OK)
            dialog.set_title("Could not download video")
            response = dialog.run()
            if response == -5:
                dialog.destroy()
        entry_url.set_text("")
        entry_url.grab_focus()

    def menu_file_open_clicked(self, widget):
        filechooser = self.get_widget(widget, "filechooserdialog")
        filechooser.set_current_folder(os.path.expanduser("~"))
        filechooser.show()

    def menu_help_info_clicked(self, widget):
        aboutdialog = self.get_widget(widget, "aboutdialog")
        aboutdialog.show()

    def on_entry_url_editing_done(self, widget):
        entry_url = self.get_widget(widget, "entry_url")
        entry_content = entry_url.get_text()
        self.__download(entry_content)

    def fc_button_open_file_clicked(self, widget): # Chose file in filechooserdialog and pressed "Open"
        filechooser = self.get_widget(widget, "filechooserdialog")
        filechooser.hide()
        vdown_path = self.config.get("vdown", "path")
        self.chosen_file = filechooser.get_filename()
        videofiles = []
        print "%s selected." % self.chosen_file
        filechooser.hide()
        print "Downloading a list..."
        os.chdir(os.path.expanduser("~"))   # Change to Home Directory of the user, where the videos shall be saved 
        file = open(self.chosen_file, "r")
        i = 0
        while 1: 
            line = file.readline()
            if not line:
                break
            if line[-1] == "\n":
                line = line[:-1]
            if os.path.isfile("/tmp/vdown.last"):
                os.remove("/tmp/vdown.last")
            print "Trying to download %s..." % line
            vdown_command = vdown_path," ",line
            try:
                process = Popen(vdown_command)
            except:
                print "Could not execute %s!" % vdown_path
                print "Exact command: ",vdown_command               
                print "Error: ",exc_info()
            else:
                while process.returncode == None:
                    gtk.main_iteration_do(False)
                gtk.main_iteration_do(True)
            if os.path.isfile("/tmp/vdown.last"):
                last = open("/tmp/vdown.last", "r")
                videofile = last.read()
                videofiles.append(videofile)
                i += 1
                last.close()
                print "Downloaded video successfully and saved it as %s" % videofile
            else:
                print "Error while downloading file... Trying next line (if any)..."
        print "=============================="
        if i >= 1:
            videofiles_as_list = "".join(videofiles)
            print videofiles_as_list
            print "Downloaded %s files succesfully." % i
            msg = "Downloaded "+str(i)+" video(s) successfully. Its/Their names: \n"+videofiles_as_list
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                   message_format=msg,
                                   buttons=gtk.BUTTONS_OK)
            dialog.set_title("Downloaded videos.")
            dialog.run()
            dialog.destroy()
        else: # NO video downloaded!
            print "Damn... no video could be downloaded!"
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
                                   message_format="NO video could be downloaded! \nThe list file you specified: "+self.chosen_file,
                                   buttons=gtk.BUTTONS_OK)
            dialog.set_title("Could not downloaded videos!")
            dialog.run()
            dialog.destroy()
        file.close()

    def fc_button_cancel_clicked(self, widget): # Clicked "Cancel" in filechooser
        filechooser = self.get_widget(widget, "filechooserdialog")
        filechooser.hide()

    def closedSomehow(self, widget, event = None):
        gtk.main_quit()

    def on_aboutdialog_delete(self, widget, event):
        aboutdialog = self.get_widget(widget, "aboutdialog")
        aboutdialog.hide()

    def on_filechooserdialog_delete(self, widget):
        filechooser = self.get_widget(widget, "filechooserdialog")
        filechooser.hide()

if __name__ == "__main__":
    print """
Do _not_ run this file directly!
    """
