import gtk.glade
import handler

class GUI_Handler(handler.Handler):
    def __init__(self):
        handler.Handler.__init__(self)
        self.__file = None

    def on_menu_file_open_activate(self, mi):
        fc = self.get_widget(mi, "filechooserdialog")
        fc.show()

    def on_button_open_file_clicked(self, button):
        fc = self.get_widget(button, "filechooserdialog")
        self.__file = fc.get_filename()
        print self.__file
        fc.hide() 
    
    
if __name__ == "__main__":
    print """
do not run this file directly
    """
