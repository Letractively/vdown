import os
import sys
import ConfigParser

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

if __name__ == "__main__":
    print """
do not run this file directly

    """
