# Kabikaboo statistics window
#
# Novel Writing Assistance Software
# Copyleft (c) 2009
# Created by David Glen Kerr
# Naturally Intelligent Inc.
#
# Free and Open Source
# Licensed under GPL v2 or later
# No Warranty

from file import KabikabooFile
#from kabikaboo import KabikabooMainWindow
import os
import sys
import time
import gtk
import pango
import pygtk
import glib

class KabikabooStatisticsWindow:
    # init main window
    def __init__(self):
        # create gtk builder
        self.builder = gtk.Builder()
        # load interface
        if os.path.isfile(os.path.join("ui", "statistics.glade")):
            self.builder.add_from_file(os.path.join("ui", "statistics.glade"))
        elif os.path.isfile(os.path.join("..", "ui", "statistics.glade")):
            self.builder.add_from_file(os.path.join("..", "ui", "statistics.glade"))
        elif os.path.isfile("/usr/share/kabikaboo/ui/statistics.glade"):
            self.builder.add_from_file("/usr/share/kabikaboo/ui/statistics.glade")
        # find main window
        self.window = self.builder.get_object("window_statistics")
        # pointers, must be set
        self.file = None
        self.kabikaboo = None
        self.document = None
        # application icon
        if os.path.isfile("kabikaboo.png"):
            gtk.window_set_default_icon_from_file("kabikaboo.png")
        elif os.path.isfile(os.path.join("..", "kabikaboo.png")):
            gtk.window_set_default_icon_from_file(os.path.join("..", "kabikaboo.png"))
        elif os.path.isfile("/usr/src/kabikaboo/kabikaboo.png"):
            gtk.window.set_default_icon_from_file("/usr/src/kabikaboo/kabikaboo.png")
        # data
        self.start_word_count = 0
        self.session_word_count = 0
        self.words_per_minute = 0
        self.start_time = time.time()
        self.session_time = time.time()
        # connect gui callbacks
        self.connect_gui()

    def set_data(self, kabikaboo, file, document):
        self.file = file
        self.kabikaboo = kabikaboo
        self.document = document
        # stats from document
        if not self.file.calculate_statistics:
            self.start_word_count = self.document.word_count()
        else:
            self.start_time = self.kabikaboo.start_time
            if self.kabikaboo.start_word_count == -1:
                self.kabikaboo.start_word_count = self.document.word_count()
            self.start_word_count = self.kabikaboo.start_word_count                
        self.update_title()
        # display
        self.display_statistics()
        # timer
        glib.timeout_add(250, self.display_statistics) 
        self.set_window_title()

    def set_window_title(self):
        if self.file.show_application_name and self.file.application_name != '':
            self.window.set_title(self.file.application_name + ' - Statistics')
        else:
            self.window.set_title(self.document.title + ' - Statistics')

    def update_title(self):
        # now calculate them (potentially)
        label_header = self.builder.get_object("label_header")
        label_header.set_markup('<b><u>' + self.document.get_title() + ' - Statistics</u></b>')

    def new_data(self, document):
        self.document = document
        # stats from document
        self.start_time = self.kabikaboo.start_time
        if not self.file.calculate_statistics:
            self.start_word_count = self.document.word_count()
        else:
            if self.kabikaboo.start_word_count == -1:
                self.kabikaboo.start_word_count = self.document.word_count()
            self.start_word_count = self.kabikaboo.start_word_count                

    def connect_gui(self):
        #close button
        close_button = self.builder.get_object("button_close")
        close_button.connect("clicked", self.closed_button_callback)
        #labels
        self.label_last_word_count_number = self.builder.get_object("label_last_word_count_number")
        self.label_current_word_count_number = self.builder.get_object("label_current_word_count_number")
        self.label_session_word_count_number = self.builder.get_object("label_session_word_count_number")
        self.label_session_time_number = self.builder.get_object("label_session_time_number")
        self.label_wpm_number = self.builder.get_object("label_wpm_number")
        self.label_node_words_number = self.builder.get_object("label_node_words_number")

    # close
    def closed_button_callback(self, data=None):
        self.window.hide()

    # calculate statistics and save in document
    def display_statistics(self):
        # derive stats
        self.current_word_count = self.document.word_count()
        self.session_word_count = self.current_word_count - self.start_word_count
        self.session_time = time.time() - self.start_time
        self.words_per_minute = self.session_word_count / max(self.session_time/60, 1)
        # display
        self.label_last_word_count_number.set_text("%d" % self.start_word_count)
        self.label_current_word_count_number.set_text("%d" % self.current_word_count)
        self.label_session_word_count_number.set_text("%d" % self.session_word_count)
        if self.session_time < 60*60:
            self.label_session_time_number.set_text(time.strftime("%M:%S", time.gmtime(self.session_time)))
        else:
            self.label_session_time_number.set_text(time.strftime("%H:%M:%S", time.gmtime(self.session_time)))
        self.label_wpm_number.set_text("%d" % self.words_per_minute)
        if self.kabikaboo.editor_node:
            self.label_node_words_number.set_text("%d" % self.kabikaboo.editor_node.visible_word_count(False))
        else:
            self.label_node_words_number.set_text("n/a")
        # return true for timer to repeat
        return True
