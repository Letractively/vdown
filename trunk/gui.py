#!/usr/bin/env python2.5
# -*- coding: UTF-8 -*-

#***************************************************************************\
#*   Copyright (C) 2007 by Nicolai Spohrer,                                *
#*   nicolai@xeve.de                                                       *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU General Public License for more details.                          *
#*                                                                         *
#*   You should have received a copy of the GNU General Public License     *
#*   along with this program; if not, see                                  *
#*   <http://www.gnu.org/licenses/gpl.html> or write to the                *
#*   Free Software Foundation, Inc.,                                       *
#*   59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.             *
#***************************************************************************
# Filename   : gui.py                                                      *
# Description: Downloads videos from video sharing websites like YouTube,  *
#       Myspace Video, Google Video, Clipfish and so on.                   *
# This application uses <videograb.de>                                     *
# The video will be saved as FLV file.                                     *
#***************************************************************************/

import os, sys, re

try:
    import pygtk
    pygtk.require("2.0")
except:
    print "PyGTKv2 needed"
    sys.exit(1)

try:
    import gtk
    import gtk.glade
except:
    sys.exit(1)

from time import sleep
from main import fdownload
from main import convert
from main import configuration
from main import get_data
from main import folder_is_writable
import gettext
from user import home as userhome

gladefile = "gvdown.glade"

# <Translation stuff>

APP = "gvdown"
DIR = "po"

gtk.glade.bindtextdomain(APP, DIR)
gtk.glade.textdomain(APP)

# </Translation stuff>

class gui:
    def __init__(self):
        self.wTree = gtk.glade.XML(gladefile)
        dic = {"closedSomehow" : self.closedSomehow,
                "download_single" : self.download_single,
                "menu_help_info_clicked" : self.menu_help_info_clicked,
                "on_aboutdialog_delete" : self.on_aboutdialog_delete,
                "menu_file_open_clicked" : self.menu_file_open_clicked,
                "fc_open_file_clicked" : self.fc_open_clicked,
                "fc_cancel_clicked" : self.fc_cancel_clicked,
                "on_filechooserdialog_delete" : self.on_filechooserdialog_delete,
                "menu_file_settings_clicked" : self.menu_file_settings_clicked,
                "on_swindow_delete" : self.on_swindow_delete,
                "swindow_close_clicked" : self.swindow_close_clicked}
        self.wTree.signal_autoconnect(dic)

        self.config = configuration()
        self.config.readconfig()

        self.listdownloading = False

        if not os.path.isdir(self.config.get("general", "save_videos_in")):
            try:
                os.mkdir(self.config.get("general", "save_videos_in"))
            except OSError:
                print _("Could not create the directory where the videos shall be saved in (specified in %(configfile)s)! Check permissions.") % {"configfile" : os.path.join(userhome, ".gvdownrc")}
                sys.exit(1)
        if not folder_is_writable(self.config.get("general", "save_videos_in")):
            print _("Cannot write to video output directoy! Check permissions or change the directory in %(configfile)s") % {"configfile" : os.path.join(userhome, ".gvdownrc")}
            sys.exit(1)

    def closedSomehow(self, widget, event = None):
        gtk.main_quit()

    def download_single(self, widget, event = None):
        entry_url = self.wTree.get_widget("entry_url")
        pb = self.wTree.get_widget("dprogressbar")
        mainDownload_button = self.wTree.get_widget("mainDownload_button")
        mainClose_button = self.wTree.get_widget("mainClose_button")
        url = entry_url.get_text()
        os.chdir(self.config.get("general", "save_videos_in"))
        pb.set_fraction(0)
        pb.set_text(_("Fetching video information..."))
        if url == "":
            pb.set_text(_("No URL specified"))
        else:
            print "----"
            print _("Trying to download %(url)s") % {"url" : url}
            pb.set_fraction(0)
            mainDownload_button.set_sensitive(False)
            mainClose_button.set_sensitive(False)
            data = get_data(url)
            data.start()
            while data.status == -1:
                gtk.main_iteration_do(False)
                sleep(0.01)
            gtk.main_iteration_do(True)
            if data.status == 0:
                saveAs = os.path.join(self.config.get("general", "save_videos_in"), data.data[2])
                print "Saving file as \"%(filename)s\"..." % {"filename" : saveAs}
                down = fdownload(data.data[0], data.data[2])
                down.start()
                pb.set_fraction(0)
                pb.set_text(_("Downloading video..."))
                progress = down.downloaded()/100
                while down.get_filesize() == 0:
                    gtk.main_iteration_do(False)
                    sleep(0.01)
                gtk.main_iteration_do(True)
                filesize = down.get_filesize()
                print "Filesize: %(filesize)s KB" % {"filesize" : filesize}
                while progress < 1:
                    gtk.main_iteration_do(False)
                    sleep(0.01)
                    pb.set_fraction(progress)
                    progress = down.downloaded()/100
                gtk.main_iteration_do(True)
                pb.set_fraction(1)
                pb.set_text(_("Download finished."))
                if self.config.getboolean("general", "convert") and data.data[3]:
                    pb.set_text(_("Converting file"))
                    output = convert(saveAs, self.config.get("general", "convert_filename_extension"), self.config.get("general", "convertcmd"))
                    output.start()
                    while output.status == -1:
                        gtk.main_iteration_do(False)
                        sleep(0.01)
                    gtk.main_iteration_do(True)
                    pb.set_text(_("Converted file."))
                    if self.config.getboolean("general", "delete_source_file_after_converting"):
                        os.remove(saveAs)
                        print _("Deleted input (.flv) file")
            else:
                pb.set_text(_("Wrong URL / unsupported video portal"))
            mainDownload_button.set_sensitive(True)
            mainClose_button.set_sensitive(True)
            print "----"

##

    def menu_help_info_clicked(self, widget, event = None):
        aboutdialog = self.wTree.get_widget("aboutdialog")
        aboutdialog.show()

    def on_aboutdialog_delete(self, widget, event):
        aboutdialog = self.wTree.get_widget("aboutdialog")
        aboutdialog.hide()
        return True

##

    def menu_file_open_clicked(self, widget):
        fc = self.wTree.get_widget("filechooserdialog")
        fc.set_current_folder(userhome)
        fc.show()

    def on_filechooserdialog_delete(self, widget, event):
        print "fcdelete"
        fc = self.wTree.get_widget("filechooserdialog")
        fc.hide()
        return True

    def fc_cancel_clicked(self, widget): # Clicked on button 'cancel' in filechooserdialog
        fc = self.wTree.get_widget("filechooserdialog")
        fc.hide()

    def fc_open_clicked(self, widget):
        if self.listdownloading == False:
            self.download_list()

    def download_list(self): # Clicked on button 'open' in filechooserdialog
        self.listdownloading = True
        fc = self.wTree.get_widget("filechooserdialog")
        pb = self.wTree.get_widget("dprogressbar")
        mainDownload_button = self.wTree.get_widget("mainDownload_button")
        mainClose_button = self.wTree.get_widget("mainClose_button")
        os.chdir(self.config.get("general", "save_videos_in"))
        fc.hide()
        pb.set_fraction(0)
        chosen_list = fc.get_filename()
        print "%(list)s selected" % {"list" : chosen_list}
        print "-----"
        mainDownload_button.set_sensitive(False)
        mainClose_button.set_sensitive(False)
        pb.set_text(_("Downloading a list..."))
        file = open(chosen_list, "r")
        i = 0
        successful = 0 # videos downloaded successfully
        while True:
            pb.set_fraction(0)
            pb.set_text(_("Fetching video information..."))
            line = file.readline()
            if not line:
                break
            if line[-1] == "\n":
                line = line[:-1]
            print "----"
            print _("Trying to download %(link)s") % {"link" : line}
            v_no = i+1 # example: You're downloading the v_no. video && You're downloading the 5. video
            data = get_data(line)
            data.start()
            while data.status == -1:
                gtk.main_iteration_do(False)
                sleep(0.01)
            gtk.main_iteration_do(True)
            if data.status == 0:
                saveAs = os.path.join(self.config.get("general", "save_videos_in"), data.data[2])
                print _("Saving file as \"%(filename)s\"...") % {"filename" : saveAs}
                down = fdownload(data.data[0], data.data[2])  # (http://*.*/*, *.flv)
                down.start()
                pb.set_text(_("Downloading video %(number)s") % {"number" : v_no})
                progress = down.downloaded()/100
                while down.get_filesize() == 0:
                    gtk.main_iteration_do(False)
                    sleep(0.01)
                gtk.main_iteration_do(True)
                filesize = down.get_filesize()
                print _("Filesize: %(filesize)s KB") % {"filesize" : filesize}
                while progress < 1:
                    gtk.main_iteration_do(False)
                    sleep(0.005)
                    pb.set_fraction(progress)
                    progress = down.downloaded()/100
                gtk.main_iteration_do(True)
                pb.set_fraction(1)
                pb.set_text(_("Finished download #%(number)s") % {"number" : v_no})
                successful += 1
                if self.config.getboolean("general", "convert") and data.data[3]:
                    pb.set_text(_("Converting file"))
                    output = convert(saveAs, self.config.get("general", "convert_filename_extension"), self.config.get("general", "convertcmd"))
                    output.start()
                    while output.status == -1:
                        gtk.main_iteration_do(False)
                        sleep(0.01)
                    gtk.main_iteration_do(True)
                    pb.set_text(_("Converted file."))
                    if self.deletesourcefile:
                        os.remove(saveAs)
                        print _("Deleted input (.flv) file")
            else:
                print _("Wrong URL / unsupported video portal")
                pb.set_text(_("Download #%(number)s failed") % {"number" : v_no})
            i += 1
            print "----"
        pb.set_text(_("%(successful)s of %(all)s successful") % {"successful" : successful, "all" : i})
        mainDownload_button.set_sensitive(True)
        mainClose_button.set_sensitive(True)
        self.listdownloading = False
        print "-----"

##

    def menu_file_settings_clicked(self, widget):
        swindow = self.wTree.get_widget("settingswindow")
        sfcb = self.wTree.get_widget("sfcb") # settings filechooser button
        convertbutton = self.wTree.get_widget("convertbutton")
        convertcmdentry = self.wTree.get_widget("convertcmdentry")
        fextension_entry = self.wTree.get_widget("fextension_entry")
        deletesourcefilebutton = self.wTree.get_widget("deletesourcefilebutton")
        sfcb.set_local_only(True)
        sfcb.set_show_hidden(False)
        sfcb.set_current_folder(self.config.get("general", "save_videos_in"))
        convertbutton.set_active(self.config.getboolean("general", "convert"))
        convertcmdentry.set_text(self.config.get("general", "convertcmd"))
        fextension_entry.set_text(self.config.get("general", "convert_filename_extension"))
        deletesourcefilebutton.set_active(self.config.getboolean("general", "delete_source_file_after_converting"))
        swindow.show()

    def on_swindow_delete(self, widget, event):
        swindow = self.wTree.get_widget("settingswindow")
        swindow.hide()
        return True

    def swindow_close_clicked(self, widget):
        sfcb = self.wTree.get_widget("sfcb")
        swindow = self.wTree.get_widget("settingswindow")
        convertcmdentry = self.wTree.get_widget("convertcmdentry")
        convertbutton = self.wTree.get_widget("convertbutton")
        fextension_entry = self.wTree.get_widget("fextension_entry")
        deletesourcefilebutton = self.wTree.get_widget("deletesourcefilebutton")
        outputdir = sfcb.get_filename()
        if convertbutton.get_active():
            self.config.set("general", "convert", "yes")
        else:
            self.config.set("general", "convert", "no")
        convertcmd = convertcmdentry.get_text()
        self.config.set("general", "convertcmd", convertcmd)
        self.config.set("general", "convert_filename_extension", fextension_entry.get_text())
        deletesourcefile = deletesourcefilebutton.get_active()
        if deletesourcefile:
            self.config.set("general", "delete_source_file_after_converting", "yes")
        else:
            self.config.set("general", "delete_source_file_after_converting", "no")
        self.config.write_config()
        if not folder_is_writable(outputdir):
            print _("Cannot write to video output folder. Choose another.")
        else:
            self.config.set("general", "save_videos_in", outputdir)
            self.config.write_config()
            swindow.hide()

##

if __name__ == "__main__":
    try:
        fileread = open(gladefile)
        fileread.close()
    except:
        print _("Could not open %(gladefile)s") % {"gladefile" : gladefile}
        sys.exit(1)

app = gui()
gtk.main()
