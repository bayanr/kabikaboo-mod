# Kabikaboo file handler
#
# Novel Writing Assistance Software
# Copyleft (c) 2009
# Created by David Kerr
# Naturally Intelligent Inc.
#
# Free and Open Source
# Licensed under GPL v2 or later
# No Warranty

from document import current_version
from document import KabikabooDocument
from ConfigParser import *
# pickle file handling (awesome)
import pickle
import os.path
import re

class KabikabooFile:
    # initialize
    def __init__(self):
        home = os.path.expanduser('~')
        self.application_name = 'Kabikaboo'
        self.show_application_name = True
        self.recovery_file = os.path.join(home, '.kabikaboo', 'recovery.txt')
        self.settings_file = os.path.join(home, '.kabikaboo', 'settings.txt')
        self.working_file = ''
        self.last_directory = os.path.join(home, 'Documents')
        self.last_import_directory = os.path.join(home, 'Documents')
        self.last_export_directory = os.path.join(home, 'Documents')
        self.history = []
        self.max_history = 5
        self.different = False
        self.window_maximized = False
        self.remember_position = False
        self.window_x = -1
        self.window_y = -1
        self.diff_x = 0
        self.diff_y = 0
        self.window_width = 800
        self.window_height = 550
        self.attribute_panel_height = 150
        self.tree_width = 250
        self.tool_text = False
        self.show_tabs = True
        self.show_node_path = False
        self.show_node_path_status = True
        self.homog_tabs = False
        self.show_tab_arrows = True
        self.show_bullets = False
        self.show_attributes = True
        self.show_statusbar = True
        self.show_toolbar_tree = True
        self.show_toolbar_text = False
        self.show_file_status = True
        self.show_directory_status = True
        self.move_on_new = False
        self.sample_data = True
        self.tab_bullets = False
        self.calculate_statistics = False
        self.fullscreen = False
        self.spellcheck = False # can hurt app speed, even on the sample data
        self.tree_toolbar_intree = False
        # loading, etc
        self.load_file_message = ''
        self.opened_attempts = 0
        self.max_open_attempts = 2
        self.upgraded = False
        self.proper_shutdown = True
        self.autoopen = True
        self.save_on_exit = False
        self.autosave = False
        self.autosave_interval = 5
        self.autosave_version = False
        self.spaces_above=2
        self.spaces_below=2
        # load settings (must do this last, after setting default values)
        self.load_settings(self.settings_file)
        # load recovery
        self.load_recovery()
        if not self.proper_shutdown:
            print 'Improper shutdown detected...'
        self.save_recovery(False)
        # settings
        self.check_settings_dir()

    def check_settings_dir(self):
        home = os.path.expanduser('~')
        if not os.path.isdir(os.path.join(home, '.kabikaboo')):
            os.mkdir(os.path.join(home, '.kabikaboo'))

    def new(self, document):
        document.new_document()
        self.working_file = ''

    def open(self, document):
        if self.autoopen and self.working_file != '':
            return self.load_last_saved()
        else:
            return False, document

    def close(self, document):
        if self.save_on_exit and self.working_file != '':
            self.save_last_opened(document)

    def load_last_saved(self):
        return self.load_from_file_pickle(self.working_file)

    def save(self, document):
        result = False
        if self.save_to_file_pickle(self.working_file, document):
            result = True
        return result

    def save_last_saved(self, document):
        result = False
        if self.save_to_file_pickle(self.working_file, document):
            result = True
        return result

    def save_last_opened(self, document):
        result = False
        if self.save_to_file_pickle(self.working_file, document):
            result = True
        return result

    # autonumbered save based on document title
    def save_version(self, document):
        result = False
        title = document.title.replace(' ', '')
        if title == '' or len(title)<1:
            title = 'Unnamed'
        version = 1
        # need to check all files first and find the last version number
        #  user may have deleted or moved earlier versions
        existing_files = os.listdir(self.last_directory)
        for existing_file in existing_files:
            # find end of DocumentTitle-
            index1 = existing_file.find(title + '-') + len(title + '-')
            # find start of .kaboo
            index2 = existing_file.find('.kaboo')
            # get text between
            if index1>0 and index2>0 and index2>index1:
                try:
                    old_version = int(existing_file[index1:index2])
                    if old_version >= version:
                        version = old_version + 1
                except ValueError:
                    pass
        if version < 1:
            version = 1
        # now we have our best guess at a file name
        filename = title + '-' + str(version).zfill(2) + '.kaboo'
        # double check for duplicates
        while os.path.isfile(filename):
            version = version + 1
            filename = title + '-' + str(version).zfill(2) + '.kaboo'
        # finally, save our file
        final_file = self.last_directory + filename
        if self.save_to_file_pickle(final_file, document):
            self.working_file = final_file
            result = True
        # return the version for status message
        return result, version

    # save to .kaboo file
    def save_to_file(self, filename, document):
        result = False
        self.last_directory = os.path.dirname(filename) + os.sep
        if self.save_to_file_pickle(filename, document):
            result = True
        return result

    # save copy to .kaboo file
    def save_copy_to_file(self, filename, document):
        result = False
        current_working_file = self.working_file
        if self.save_to_file_pickle(filename, document):
            result = True
        self.working_file = current_working_file
        return result

    # load from .kaboo file
    def load_from_file(self, filename):
        result = False
        result, document = self.load_from_file_pickle(filename)
        self.last_directory = os.path.dirname(filename) + os.sep
        if result:
            result = True
        return result, document

    # load from pickle.kaboo file
    def load_from_file_pickle(self, filename):
        result = False
        self.load_file_message = ''
        self.upgraded = False
        if os.path.isfile(filename):
            input = open(filename)
            if input:
                try:
                    document = pickle.load(input)
                except:
                    print 'Invalid file.'
                    return result, None
                old_document = None
                # test document version 1.1 (when version was added)
                try:
                    document.version
                except AttributeError:
                    # this is 1.0 or earlier, upgrade to 1.1
                    self.load_file_message += "Old file version detected (1.0)...\n"
                    if not self.upgraded:
                        old_document = document
                    document.version = current_version()
                    document.tab_max = 5
                    document.tabs = []
                    document.version = '1.1'
                    self.load_file_message += "Upgrading to version 1.1 (added tabs)...\n"
                    self.upgraded = True
                # 1.1 to 1.1.1 upgrade
                if document.version == '1.1':
                    self.load_file_message += "Old file version detected (1.1)...\n"
                    if not self.upgraded:
                        old_document = document
                    document.tab_max = 7
                    document.version = '1.1.1'
                    self.load_file_message += "Upgrading to version 1.1.1 (extra tabs)...\n"
                    self.upgraded = True
                # 1.2
                if document.version == '1.1' or document.version == '1.1.1' or document.version <= 1.1:
                    self.load_file_message += "Old file version detected (1.1.1)...\n"
                    if not self.upgraded:
                        old_document = document
                    document.add_bulleting()
                    document.version = '1.2'
                    self.load_file_message += "Upgrading to version 1.2 (added bulleting)...\n"
                    self.upgraded = True
                # 1.4
                if document.version == '1.2':
                    document.version = '1.4'
                # 1.5
                if document.version == '1.4':
                    self.load_file_message += "Old file version detected (1.4)...\n"
                    if not self.upgraded:
                        old_document = document
                    document.bookmarks = []
                    document.bookmark_max = 10
                    document.show_titles_in_view = True
                    document.show_titles_in_export = True
                    document.version = '1.5'
                    self.load_file_message += "Upgrading to version 1.5 (added bookmarks)...\n"
                    self.upgraded = True                    
                # 1.7
                # 1.7 test one
                upgrade_17_needed = False
                if document.version == '1.5' or document.version == '1.6':
                    upgrade_17_needed = True
                if not upgrade_17_needed:
                    # test for visits in root node
                    try:
                        if document.visits_all == 1:
                            pass
                    except AttributeError:
                        upgrade_17_needed = True
                if upgrade_17_needed:
                    self.load_file_message += "Old file version detected (1.5/1.6)...\n"
                    if not self.upgraded:
                        old_document = document
                    document.add_visits_data()
                    document.version = '1.7'
                    self.load_file_message += "Upgrading to version 1.7 (added recently visited)...\n"
                    self.upgraded = True
                # show warning in console (also passed to GUI)
                if self.upgraded:
                    self.load_file_message = "Kabikaboo Upgrade Notice\n\nYour file was saved with an older version of Kabikaboo.\n" + self.load_file_message
                    self.load_file_message += "Upgraded file: %s" % filename + "\n"
                    backupfile = filename + '.backup~'
                    if self.save_to_file_pickle(backupfile, old_document):
                        self.load_file_message += "\nSaved copy of original for backup: %s" % backupfile + "\n"
                        self.add_to_history(backupfile)
                    self.load_file_message += "\nThe upgraded changes are not permanent until saved.\n"
                    self.load_file_message += "It is recommended to save your document with a new versioned filename.\n"
                # set variables
                self.working_file = filename
                self.add_to_history(filename)
                print self.load_file_message
                result = True
                input.close
        return result, document

    # save to pickle.kaboo file
    def save_to_file_pickle(self, filename, document):
        result = False
        try:
            output = open(filename, 'w')
        except IOError:
            return result
        if output:
            pickle.dump(document, output)
            output.close
            self.working_file = filename
            self.add_to_history(filename)
            result = True
        return result

    # add to file list history
    # returns True if new, False if already in
    def add_to_history(self, filename):
        result = True
        filename = filename.replace('//', '/')
        # is this file already at the top of history?  if so skip
        if len(self.history) > 0 and self.history[0] == filename:
            return False
        # look through history for duplicate
        for search in self.history:
            # move to front
            if search == filename:
                self.history.remove(search)
                result = False
        # insert at front
        self.history.insert(0, filename)
        self.check_history()
        self.save_settings_default()
        return result

    # check history for too many files
    def check_history(self):
        # only store max histories
        while len(self.history) > self.max_history:
            del self.history[len(self.history)-1]

    def load_settings(self, filename):
        result = False
        config = ConfigParser()
        if os.path.isfile(filename):
            try:
                config.read(filename)
            except:
                print "Can't read settings file: " + filename
                return False
            # Application Settings
            if config.has_option('kabikaboo', 'application_name'):
                self.application_name = config.get('kabikaboo', 'application_name')
            if config.has_option('kabikaboo', 'last_file'):
                self.working_file = config.get('kabikaboo', 'last_file')
            if config.has_option('kabikaboo', 'last_directory'):
                self.last_directory = config.get('kabikaboo', 'last_directory')
            if config.has_option('kabikaboo', 'autoopen'):
                self.autoopen = config.getboolean('kabikaboo', 'autoopen')
            if config.has_option('kabikaboo', 'save_on_exit'):
                self.save_on_exit = config.getboolean('kabikaboo', 'save_on_exit')
            if config.has_option('kabikaboo', 'autosave'):
                self.autosave = config.getboolean('kabikaboo', 'autosave')
            if config.has_option('kabikaboo', 'autosave_interval'):
                self.autosave_interval = config.getfloat('kabikaboo', 'autosave_interval')
            if config.has_option('kabikaboo', 'autosave_version'):
                self.autosave_version = config.getboolean('kabikaboo', 'autosave_version')
            if config.has_option('kabikaboo', 'calculate_statistics'):
                self.calculate_statistics = config.getboolean('kabikaboo', 'calculate_statistics')
            # Export Settings
            if config.has_option('kabikaboo-export', 'last_export_directory'):
                self.last_export_directory = config.get('kabikaboo-export', 'last_export_directory')
            if config.has_option('kabikaboo-export', 'last_import_directory'):
                self.last_import_directory = config.get('kabikaboo-export', 'last_import_directory')
            # GUI Settings
            if config.has_option('kabikaboo-gui', 'show_application_name'):
                self.show_application_name = config.getboolean('kabikaboo-gui', 'show_application_name')
            if config.has_option('kabikaboo-gui', 'window_maximized'):
                self.window_maximized = config.getboolean('kabikaboo-gui', 'window_maximized')
            if config.has_option('kabikaboo-gui', 'remember_position'):
                self.remember_position = config.getboolean('kabikaboo-gui', 'remember_position')
            if config.has_option('kabikaboo-gui', 'window_x'):
                self.window_x = config.getint('kabikaboo-gui', 'window_x')
            if config.has_option('kabikaboo-gui', 'window_y'):
                self.window_y = config.getint('kabikaboo-gui', 'window_y')
            if config.has_option('kabikaboo-gui', 'diff_x'):
                self.diff_x = config.getint('kabikaboo-gui', 'diff_x')
            if config.has_option('kabikaboo-gui', 'diff_y'):
                self.diff_y = config.getint('kabikaboo-gui', 'diff_y')
            if config.has_option('kabikaboo-gui', 'window_width'):
                self.window_width = config.getint('kabikaboo-gui', 'window_width')
            if config.has_option('kabikaboo-gui', 'window_height'):
                self.window_height = config.getint('kabikaboo-gui', 'window_height')
            if config.has_option('kabikaboo-gui', 'tree_width'):
                self.tree_width = config.getint('kabikaboo-gui', 'tree_width')
            if config.has_option('kabikaboo-gui', 'attribute_panel_height'):
                self.attribute_panel_height = config.getint('kabikaboo-gui', 'attribute_panel_height')
            if config.has_option('kabikaboo-gui', 'tool_text'):
                self.tool_text = config.getboolean('kabikaboo-gui', 'tool_text')
            if config.has_option('kabikaboo-gui', 'show_tabs'):
                self.show_tabs = config.getboolean('kabikaboo-gui', 'show_tabs')
            if config.has_option('kabikaboo-gui', 'show_node_path'):
                self.show_node_path = config.getboolean('kabikaboo-gui', 'show_node_path')
            if config.has_option('kabikaboo-gui', 'show_node_path_status'):
                self.show_node_path_status = config.getboolean('kabikaboo-gui', 'show_node_path_status')
            if config.has_option('kabikaboo-gui', 'homog_tabs'):
                self.homog_tabs = config.getboolean('kabikaboo-gui', 'homog_tabs')
            if config.has_option('kabikaboo-gui', 'show_tab_arrows'):
                self.show_tab_arrows = config.getboolean('kabikaboo-gui', 'show_tab_arrows')
            if config.has_option('kabikaboo-gui', 'show_bullets'):
                self.show_bullets = config.getboolean('kabikaboo-gui', 'show_bullets')
            if config.has_option('kabikaboo-gui', 'show_attributes'):
                self.show_attributes = config.getboolean('kabikaboo-gui', 'show_attributes')
            if config.has_option('kabikaboo-gui', 'show_statusbar'):
                self.show_statusbar = config.getboolean('kabikaboo-gui', 'show_statusbar')
            if config.has_option('kabikaboo-gui', 'show_toolbar_tree'):
                self.show_toolbar_tree = config.getboolean('kabikaboo-gui', 'show_toolbar_tree')
            if config.has_option('kabikaboo-gui', 'show_toolbar_text'):
                self.show_toolbar_text = config.getboolean('kabikaboo-gui', 'show_toolbar_text')
            if config.has_option('kabikaboo-gui', 'show_file_status'):
                self.show_file_status = config.getboolean('kabikaboo-gui', 'show_file_status')
            if config.has_option('kabikaboo-gui', 'move_on_new'):
                self.move_on_new = config.getboolean('kabikaboo-gui', 'move_on_new')
            if config.has_option('kabikaboo-gui', 'sample_data'):
                self.sample_data = config.getboolean('kabikaboo-gui', 'sample_data')
            if config.has_option('kabikaboo-gui', 'tab_bullets'):
                self.tab_bullets = config.getboolean('kabikaboo-gui', 'tab_bullets')
            if config.has_option('kabikaboo-gui', 'fullscreen'):
                self.fullscreen = config.getboolean('kabikaboo-gui', 'fullscreen')
            if config.has_option('kabikaboo-gui', 'show_directory_status'):
                self.show_directory_status = config.getboolean('kabikaboo-gui', 'show_directory_status')
            if config.has_option('kabikaboo-gui', 'spellcheck'):
                self.spellcheck = config.getboolean('kabikaboo-gui', 'spellcheck')
            if config.has_option('kabikaboo-gui', 'tree_toolbar_intree'):
                self.tree_toolbar_intree = config.getboolean('kabikaboo-gui', 'tree_toolbar_intree')
            if config.has_option('kabikaboo-gui', 'spaces_above'):
                self.spaces_above = config.getint('kabikaboo-gui', 'spaces_above')
            if config.has_option('kabikaboo-gui', 'spaces_below'):
                self.spaces_below = config.getint('kabikaboo-gui', 'spaces_below')
            # History Settings
            if config.has_option('kabikaboo-history', 'max_history'):
                self.max_history = config.getint('kabikaboo-history', 'max_history')
            # History List
            for i in range(0, self.max_history):
                history = 'history-%d' % i
                if config.has_option('kabikaboo-history', history):
                    self.history.append(config.get('kabikaboo-history', history))
            result = True
        return result

    def save_settings_default(self):
        self.save_settings(self.settings_file)

    def save_settings(self, filename):
        result = False
        config = ConfigParser()
        config.add_section('kabikaboo')
        config.set('kabikaboo', 'application_name', self.application_name)
        config.set('kabikaboo', 'last_file', self.working_file)
        config.set('kabikaboo', 'last_directory', self.last_directory)
        config.set('kabikaboo', 'autoopen', self.autoopen)
        config.set('kabikaboo', 'save_on_exit', self.save_on_exit)
        config.set('kabikaboo', 'autosave', self.autosave)
        config.set('kabikaboo', 'autosave_interval', self.autosave_interval)
        config.set('kabikaboo', 'autosave_version', self.autosave_version)
        config.set('kabikaboo', 'calculate_statistics', self.calculate_statistics)
        config.add_section('kabikaboo-export')
        config.set('kabikaboo-export', 'last_export_directory', self.last_export_directory)
        config.set('kabikaboo-export', 'last_import_directory', self.last_import_directory)
        config.add_section('kabikaboo-gui')
        config.set('kabikaboo-gui', 'show_application_name', self.show_application_name)
        config.set('kabikaboo-gui', 'window_maximized', self.window_maximized)
        config.set('kabikaboo-gui', 'remember_position', self.remember_position)
        config.set('kabikaboo-gui', 'window_x', self.window_x)
        config.set('kabikaboo-gui', 'window_y', self.window_y)
        config.set('kabikaboo-gui', 'diff_x', self.diff_x)
        config.set('kabikaboo-gui', 'diff_y', self.diff_y)
        config.set('kabikaboo-gui', 'window_width', self.window_width)
        config.set('kabikaboo-gui', 'window_height', self.window_height)
        config.set('kabikaboo-gui', 'tree_width', self.tree_width)
        config.set('kabikaboo-gui', 'attribute_panel_height', self.attribute_panel_height)
        config.set('kabikaboo-gui', 'tool_text', self.tool_text)
        config.set('kabikaboo-gui', 'show_tabs', self.show_tabs)
        config.set('kabikaboo-gui', 'show_node_path', self.show_node_path)
        config.set('kabikaboo-gui', 'show_node_path_status', self.show_node_path_status)
        config.set('kabikaboo-gui', 'homog_tabs', self.homog_tabs)
        config.set('kabikaboo-gui', 'show_tab_arrows', self.show_tab_arrows)
        config.set('kabikaboo-gui', 'show_bullets', self.show_bullets)
        config.set('kabikaboo-gui', 'show_attributes', self.show_attributes)
        config.set('kabikaboo-gui', 'show_statusbar', self.show_statusbar)
        config.set('kabikaboo-gui', 'show_toolbar_tree', self.show_toolbar_tree)
        config.set('kabikaboo-gui', 'show_toolbar_text', self.show_toolbar_text)
        config.set('kabikaboo-gui', 'show_file_status', self.show_file_status)
        config.set('kabikaboo-gui', 'show_directory_status', self.show_directory_status)
        config.set('kabikaboo-gui', 'move_on_new', self.move_on_new)
        config.set('kabikaboo-gui', 'sample_data', self.sample_data)
        config.set('kabikaboo-gui', 'tab_bullets', self.tab_bullets)
        config.set('kabikaboo-gui', 'fullscreen', self.fullscreen)
        config.set('kabikaboo-gui', 'spellcheck', self.spellcheck)
        config.set('kabikaboo-gui', 'tree_toolbar_intree', self.tree_toolbar_intree)
        config.set('kabikaboo-gui', 'spaces_above', self.spaces_above)
        config.set('kabikaboo-gui', 'spaces_below', self.spaces_below)
        config.add_section('kabikaboo-history')
        config.set('kabikaboo-history', 'max_history', self.max_history)
        for index, file in enumerate(self.history):
            config.set('kabikaboo-history', 'history-%d' % index, file)
        try:
            output = open(filename, 'w')
            config.write(output)
            result = True
        except:
            print "Can't write settings file: " + filename
        return result

    def export_to_text_file(self, document, node, filename, recurse=True, show_titles=True):
        try:
            output = open(filename, 'w')
        except:
            print "Can't write text file: " + filename
            return False
        output.write(node.export_text('', recurse, show_titles))
        self.last_export_directory = os.path.dirname(filename) + os.sep
        self.save_settings_default()
        return True

    def export_to_html_file(self, document, node, filename, recurse=True, show_titles=True):
        try:
            output = open(filename, 'w')
        except:
            print "Can't write HTML file: " + filename
            return False
        output.write(node.html_text(recurse, show_titles))
        self.last_export_directory = os.path.dirname(filename) + os.sep
        self.save_settings_default()
        return True

    def load_recovery(self):
        result = False
        config = ConfigParser()
        if os.path.isfile(self.recovery_file):
            try:
                config.read(self.recovery_file)
            except:
                print "Can't read recovery file: " + self.recovery_file
                return False
            if config.has_option('kabikaboo-recovery', 'closed'):
                self.proper_shutdown = config.getboolean('kabikaboo-recovery', 'closed')
            if config.has_option('kabikaboo-recovery', 'opened-attempts'):
                self.opened_attempts = config.getint('kabikaboo-recovery', 'opened-attempts')
            result = True
        return result

    def save_recovery(self, closed):
        result = False
        config = ConfigParser()
        config.add_section('kabikaboo-recovery')
        config.set('kabikaboo-recovery', 'closed', closed)
        if closed:
            self.opened_attempts = 0
        config.set('kabikaboo-recovery', 'opened-attempts', self.opened_attempts)
        try:
            output = open(self.recovery_file, 'w')
            config.write(output)
            result = True
        except:
            print "Can't write recovery file: " + self.recovery_file
        return result

    # import a text file
    def import_text_file(self, filename, node):
        result = False
        file = open(filename)
        if file:
            while 1:
                line = file.readline()
                if not line:
                    break
                node.text += line
            result = True
        return result
