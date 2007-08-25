import gtk.glade
import handler
import os

class GUI_Handler(handler.Handler):
    def __init__(self):
        handler.Handler.__init__(self)
        self.__file = None

    def menu_file_open_clicked(self, widget, event):
        filechooser = self.get_widget(widget, "filechooserdialog")
        filechooser.set_current_folder(os.path.expanduser("~"))
        filechooser.show()

    def menu_help_info_clicked(self, widget, event):
        aboutdialog = self.get_widget(widget, "aboutdialog")
        aboutdialog.show()

    def on_fc_button_open_file_clicked(self, widget): # Chose file in filechooserdialog and pressed "Open"
        filechooser = self.get_widget(widget, "filechooserdialog")
        self.chosen_file = filechooser.get_filename()
        print "%s selected." % self.chosen_file
        filechooser.hide()

    def on_fc_button_cancel_clicked(self, widget): # Clicked "Cancel" in filechooser
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

    def mainDownload_button_clicked(self, widget):
        entry_url = self.get_widget(widget, "entry_url")
        entry_content = entry_url.get_text()
        print 'You entered: "%s"' % entry_content

if __name__ == "__main__":
    print """
do not run this file directly
    """
