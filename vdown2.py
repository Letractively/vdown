import gtk
import controller
import vdown_handler

class GUI(controller.Controller):
    """"""
    def __init__(self):
        super(GUI, self).__init__("vdown_config",
                                  "vdown.glade",
                                  "window", debug=0)
        self.__setup()

    def __setup(self):
        handler = vdown_handler.GUI_Handler()
        self.check_handler(handler)
        self.w_root.show()

if __name__ == "__main__":
    run = GUI()
    gtk.main()
