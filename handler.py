import sys
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
    def __init__(self):
        pass

    def get_widget(self, current_widget, name):
        xml_glade = gtk.glade.get_widget_tree(current_widget)
        widget = xml_glade.get_widget(name)
        return widget

if __name__ == "__main__":
    print """
do not run this file directly
    """