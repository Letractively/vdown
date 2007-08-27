import sys
import config

try:
    import pygtk
    pygtk.require("2.0")
except:
    pass
try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

class Handler(object):
    def __init__(self, config_file=None):
        if config_file:
            self.config = config.Config()
            self.config.read(config_file)

    def get_widget(self, current_widget, name):
        xml_glade = gtk.glade.get_widget_tree(current_widget)
        widget = xml_glade.get_widget(name)
        return widget

if __name__ == "__main__":
    print """
Do _not_ run this file directly!
    """
