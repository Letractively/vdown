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

import os
import config
import xml.parsers.expat

class Controller(object):
    """This is an Hello World GTK application"""
    def __init__(self, config_file, xml_filename, xml_root, debug=0):
        self.__config_file = config_file
        self._config = None
        self.__xml_filename = xml_filename
        self.__xml_root = xml_root
        self._debug = debug
        self.__tree_obj = None
        self.__connects = {}
        self.__widgets = {}
        self.__cur_handler = None
        self.w_root = None
        self.__init()

    def __init(self):
        self._config = config.Config()
        self._config.read_file(self.__config_file)
        self.__xml_file = os.path.join(self._config.get("glade", "glade_files"),
                                       self.__xml_filename)
        if not os.path.isfile(self.__xml_file):
            print "[FATAL] XML file %s does not exist." % (self.__xml_file)
            sys.exit()
        else:
            if self._debug:
                print ("XML file: %s" % (self.__xml_file))
        setattr(self, self.__xml_root, gtk.glade.XML(self.__xml_file,
                                                     self.__xml_root))
        self.__tree_obj = getattr(self, self.__xml_root)
        self.w_root = self.__tree_obj.get_widget(self.__xml_root)
        if self.w_root is None:
            print "[FATAL] root widget * %s * does not exist!!!" % (self.__xml_root)

    def __connect_signals(self, name, attrs):
        if self._debug > 1:
            print name, attrs
        if name == "signal":
            if not attrs["handler"] in self.__connects.keys():
                try:
                    obj = getattr(self.__cur_handler, attrs["handler"])
                except AttributeError, error:
                    print "Signal Handler %s doesn't exist, implement it!" % (attrs["handler"])
                else:
                    self.__connects[attrs["handler"]] = obj
        if name == "widget":
            if not attrs["id"] in self.__widgets.keys():
                setattr(self, attrs["id"], self.__tree_obj.get_widget(attrs["id"]))
            else:
                print "More than one widet of %s exists!!!" % (attrs["id"])

    def check_handler(self, handler):
        self.__cur_handler = handler
        self.__cur_handler._debug = self._debug
        self.__xml_parse = xml.parsers.expat.ParserCreate("UTF-8")
        self.__xml_parse.StartElementHandler = self.__connect_signals
        self.__xml_parse.ParseFile(open(self.__xml_file, "r"))
        if self._debug:
            print self.__connects
        if self._debug > 1:
            print self.__widgets
        self.__tree_obj.signal_autoconnect(self.__connects)

if __name__ == "__main__":
    print """
do not run this file directly
    """
