import sys
import ConfigParser
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
import xml.parsers.expat


class Config(ConfigParser.SafeConfigParser):
    """Access configuration file."""
    def __init__(self, debug=0):
        ConfigParser.SafeConfigParser.__init__(self)
        self._debug = debug

    def __check_dir(self, directory):
        """Check existence of configuration directory."""
        if not os.path.isdir(directory):
            try:
                ## create dir
                os.mkdir(directory)
            except OSError, error:
                raise error

    def read_file(self, configuration_file):
        """Read actual configuration file."""
        if os.path.isfile(configuration_file):
            ## configuration file exists
            try:
                self.read(configuration_file)
            except ConfigParser.ParsingError, error:
                raise error
        else:
            ## config file does not exists
            print "Config file %s doesn't exist" % (configuration_file)
            sys.exit(1)

    def write_file(self, configuration_file):
        """Write actual configuration to file"""
        if not os.path.dirname(configuration_file):
            configuration_file = os.path.realpath(configuration_file)
        self.__check_dir(os.path.dirname(configuration_file))
        try:
            ## overwrite existing file
            if self._debug:
                print "writing configuration file %s ..." % (configuration_file)
            self.write(open(configuration_file, "w"))
        except IOError, error:
            raise error

class Controller(object):
    def __init__(self, config_file, xml_filename, xml_root=None, debug=0):
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
        self._config = Config()
        self._config.read_file(self.__config_file)
        self.__xml_file = os.path.join(self._config.get("glade", "glade_files"),
                                       self.__xml_filename)
        if not os.path.isfile(self.__xml_file):
            print "[FATAL] XML file %s does not exist." % (self.__xml_file)
            sys.exit()
        else:
            if self._debug:
                print ("XML file: %s" % (self.__xml_file))
        setattr(self, self.__xml_root, gtk.glade.XML(self.__xml_file))
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
Do _not_ run this file directly!
    """
