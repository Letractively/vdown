import gtk
import controller
import gvdown_handler

class GUI(controller.Controller):
    """"""
    def __init__(self):
        super(GUI, self).__init__("gvdown_config",
                                  "gvdown.glade",
                                  "mainWindow", debug=0)
        self.__setup()

    def __setup(self):
        handler = gvdown_handler.GUI_Handler()
        self.check_handler(handler)
        self.w_root.show()

if __name__ == "__main__":
    run = GUI()
    gtk.main()
