import gtk.glade
import handler
import os
from sys import exc_info
from subprocess import Popen

class GUI_Handler(handler.Handler):
    def __init__(self):
        handler.Handler.__init__(self)
        self.__file = None

    def download(self, widget):
        entry_url = self.get_widget(widget, "entry_url")
        entry_content = entry_url.get_text()
        # move most of the parts below to the __download logic
        vdown_path = "/usr/bin/vdown"
        vdown_command = vdown_path," ",entry_content
        if os.path.isfile("/tmp/vdown.last"):
            os.remove("/tmp/vdown.last")
        try:
            process = Popen(vdown_command)
            process.wait()
        except:
            print "Could not execute ",vdown_path,"! Check the vdown path in gvdown_config."
            print "Error: ", exc_info()
        if os.path.isfile("/tmp/vdown.last"):
            file = open("/tmp/vdown.last", "r") # File content = video file
            savedAs = file.read()
            file.close()
            os.remove("/tmp/vdown.last")
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_INFO,
                                   message_format="Downloaded video successfully. It was saved as \""+savedAs+"\"",
                                   buttons=gtk.BUTTONS_OK)
            dialog.set_title("Downloaded video.")
            dialog.run()
            dialog.destroy()
        else: # Could not download video
            dialog = gtk.MessageDialog(type=gtk.MESSAGE_ERROR,
            message_format="The video could not be downloaded. This may be because the link was broken or the video portal is not supported (yet)\n"+"You entered: \""+entry_content+"\"",
            buttons=gtk.BUTTONS_OK)
            dialog.set_title("Could not download video")
            dialog.run()
            print dir(dialog)
            dialog.destroy()
        self.returnToMainWindow(self, widget)

    def menu_file_open_clicked(self, widget, event):
        filechooser = self.get_widget(widget, "filechooserdialog")
        filechooser.set_current_folder(os.path.expanduser("~"))
        filechooser.show()

    def menu_help_info_clicked(self, widget, event):
        aboutdialog = self.get_widget(widget, "aboutdialog")
        aboutdialog.show()

    def on_entry_url_editing_done(self, widget):
        entry_url = self.get_widget(widget, "entry_url")
        entry_content = entry_url.get_text()
        self.__download(entry_content)

    def fc_button_open_file_clicked(self, widget): # Chose file in filechooserdialog and pressed "Open"
        filechooser = self.get_widget(widget, "filechooserdialog")
        self.chosen_file = filechooser.get_filename()
        print "%s selected." % self.chosen_file
        filechooser.hide()

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

#    def mainDownload_button_clicked(self, widget):
#        self.__download(widget)
  
    def returnToMainWindow(self, event, widget):
        entry = self.get_widget(widget, "entry_url")        
        entry.set_text("")
        entry.grab_focus()

if __name__ == "__main__":
    print """
Do _not_ run this file directly!
    """
