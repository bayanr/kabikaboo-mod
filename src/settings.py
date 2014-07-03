    # Kabikaboo settings file
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
    from kabikaboo import KabikabooMainWindow
    import os
    import sys
    import gtk
    import pango
    import pygtk

    class KabikabooSettingsWindow:
        # init main window
        def __init__(self):
            # create gtk builder
            self.populating = True
            self.builder = gtk.Builder()
            # load interface
            if os.path.isfile(os.path.join("ui", "settings.glade")):
                self.builder.add_from_file(os.path.join("ui", "settings.glade"))
            elif os.path.isfile(os.path.join("..", "ui", "settings.glade")):
                self.builder.add_from_file(os.path.join("..", "ui", "settings.glade"))
            elif os.path.isfile("/usr/share/kabikaboo/ui/settings.glade"):
                self.builder.add_from_file("/usr/share/kabikaboo/ui/settings.glade")
            # find main window
            self.window = self.builder.get_object("window_settings")
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
            # connect gui callbacks
            self.connect_gui()
            self.populating = False

        def set_data(self, kabikaboo, file, document):
            self.file = file
            self.kabikaboo = kabikaboo
            self.document = document
            self.set_window_title()

        def set_window_title(self):
            if self.file.show_application_name and self.file.application_name != '':
                self.window.set_title(self.file.application_name + ' Preferences')
            else:
                self.window.set_title(self.document.title + ' Preferences')

        def connect_gui(self):
            #close button
            close_button = self.builder.get_object("button_close")
            if close_button:
                close_button.connect("clicked", self.closed_button_callback)        
            #checkbutton_openlastfile
            menu_item = self.builder.get_object("checkbutton_openlastfile")
            menu_item.connect("toggled", self.checkbutton_openlastfile_callback)        
            #checkbutton_saveonexit
            menu_item = self.builder.get_object("checkbutton_saveonexit")
            menu_item.connect("toggled", self.checkbutton_saveonexit_callback)        
            #checkbutton_autosave
            menu_item = self.builder.get_object("checkbutton_autosave")
            menu_item.connect("toggled", self.checkbutton_autosave_callback)        
            #checkbutton_autosave_version
            menu_item = self.builder.get_object("checkbutton_autosave_version")
            menu_item.connect("toggled", self.checkbutton_autosave_version_callback)        
            #checkbutton_tooltext
            menu_item = self.builder.get_object("checkbutton_tooltext")
            menu_item.connect("toggled", self.checkbutton_tooltext_callback)    
            #checkbutton_show_tabs
            menu_item = self.builder.get_object("checkbutton_show_tabs")
            menu_item.connect("toggled", self.checkbutton_show_tabs_callback)    
            #checkbutton_node_path
            menu_item = self.builder.get_object("checkbutton_node_path")
            menu_item.connect("toggled", self.checkbutton_node_path_callback)
            #checkbutton_node_path_status
            menu_item = self.builder.get_object("checkbutton_node_path_status")
            menu_item.connect("toggled", self.checkbutton_node_path_status_callback)
            #checkbutton_homog_tabs
            menu_item = self.builder.get_object("checkbutton_homog_tabs")
            menu_item.connect("toggled", self.checkbutton_homog_tabs_callback)    
            #checkbutton_tab_arrows    
            menu_item = self.builder.get_object("checkbutton_tab_arrows")
            menu_item.connect("toggled", self.checkbutton_tab_arrows_callback)    
            #checkbutton_show_bullets
            menu_item = self.builder.get_object("checkbutton_show_bullets")
            menu_item.connect("toggled", self.checkbutton_show_bullets_callback)    
            #checkbutton_attributes
            menu_item = self.builder.get_object("checkbutton_attributes")
            menu_item.connect("toggled", self.checkbutton_attributes_callback)     
            #checkbutton_file_status
            menu_item = self.builder.get_object("checkbutton_file_status")
            menu_item.connect("toggled", self.checkbutton_file_status_callback)
            #checkbutton_move_on_new
            menu_item = self.builder.get_object("checkbutton_move_on_new")
            menu_item.connect("toggled", self.checkbutton_move_on_new_callback)
            #checkbutton_sample_data
            menu_item = self.builder.get_object("checkbutton_sample_data")
            menu_item.connect("toggled", self.checkbutton_sample_data_callback)
            #checkbutton_tab_bullets
            menu_item = self.builder.get_object("checkbutton_tab_bullets")
            menu_item.connect("toggled", self.checkbutton_tab_bullets_callback)
            #checkbutton_show_titles_in_view
            menu_item = self.builder.get_object("checkbutton_show_titles_in_view")
            menu_item.connect("toggled", self.checkbutton_show_titles_in_view_callback)
            #checkbutton_show_titles_in_export
            menu_item = self.builder.get_object("checkbutton_show_titles_in_export")
            menu_item.connect("toggled", self.checkbutton_show_titles_in_export_callback)
            #checkbutton_remember_position
            menu_item = self.builder.get_object("checkbutton_remember_position")
            menu_item.connect("toggled", self.checkbutton_remember_position_callback)
            #calculate_statistics
            menu_item = self.builder.get_object("checkbutton_calculate_statistics")
            menu_item.connect("toggled", self.checkbutton_calculate_statistics_callback)
            #show_application_name
            menu_item = self.builder.get_object("checkbutton_show_application_name")
            menu_item.connect("toggled", self.checkbutton_show_application_name_callback)
            #show_directory
            menu_item = self.builder.get_object("checkbutton_show_directory")
            menu_item.connect("toggled", self.checkbutton_show_directory_callback)
            #tree_toolbar_intree
            menu_item = self.builder.get_object("checkbutton_tree_toolbar_intree")
            menu_item.connect("toggled", self.checkbutton_tree_toolbar_intree_callback)
            #entry_max_tabs
            menu_item = self.builder.get_object("spinbutton_max_tabs")
            menu_item.connect("value-changed", self.entry_max_tabs_callback)
            #entry_max_history
            menu_item = self.builder.get_object("spinbutton_max_history")
            menu_item.connect("value-changed", self.entry_max_history_callback)
            #entry_application_name
            menu_item = self.builder.get_object("entry_application_name")
            menu_item.connect("activate", self.entry_application_name_callback)
            menu_item.connect("changed", self.entry_application_name_callback)
            #entry_max_bookmarks
            menu_item = self.builder.get_object("spinbutton_max_bookmarks")
            menu_item.connect("value-changed", self.entry_max_bookmarks_callback)
            #entry_autosave_interval
            menu_item = self.builder.get_object("spinbutton_autosave_interval")
            menu_item.connect("value-changed", self.entry_autosave_interval_callback)
            #entry_max_visits
            menu_item = self.builder.get_object("spinbutton_max_visits")
            menu_item.connect("value-changed", self.entry_max_visits_callback)
            #entry_spaces_above
            menu_item=self.builder.get_object("spinbutton_spaces_above")
            menu_item.connect("value-changed", self.entry_spaces_above_callback)
            #entry_spaces_below
            menu_item=self.builder.get_object("spinbutton_spaces_below")
            menu_item.connect("value-changed", self.entry_spaces_below_callback)

        def populate_settings(self):
            self.populating = True
            #checkbutton_openlastfile
            self.builder.get_object("checkbutton_openlastfile").set_active(self.file.autoopen)
            #checkbutton_saveonexit
            self.builder.get_object("checkbutton_saveonexit").set_active(self.file.save_on_exit)
            #checkbutton_autosave
            self.builder.get_object("checkbutton_autosave").set_active(self.file.autosave)
            #checkbutton_autosave_version
            self.builder.get_object("checkbutton_autosave_version").set_active(self.file.autosave_version)
            #checkbutton_tooltext
            self.builder.get_object("checkbutton_tooltext").set_active(self.file.tool_text)
            #checkbutton_show_tabs
            self.builder.get_object("checkbutton_show_tabs").set_active(self.file.show_tabs)
            #checkbutton_node_path
            self.builder.get_object("checkbutton_node_path").set_active(self.file.show_node_path)
            #checkbutton_node_path_status
            self.builder.get_object("checkbutton_node_path_status").set_active(self.file.show_node_path_status)
            #checkbutton_homog_tabs
            self.builder.get_object("checkbutton_homog_tabs").set_active(self.file.homog_tabs)
            #checkbutton_tab_arrows
            self.builder.get_object("checkbutton_tab_arrows").set_active(self.file.show_tab_arrows)
            #checkbutton_show_bullets
            self.builder.get_object("checkbutton_show_bullets").set_active(self.file.show_bullets)
            #checkbutton_attributes
            self.builder.get_object("checkbutton_attributes").set_active(self.file.show_attributes)
            #checkbutton_file_status
            self.builder.get_object("checkbutton_file_status").set_active(self.file.show_file_status)
            #checkbutton_move_on_new
            self.builder.get_object("checkbutton_move_on_new").set_active(self.file.move_on_new)
            #checkbutton_sample_data
            self.builder.get_object("checkbutton_sample_data").set_active(self.file.sample_data)
            #checkbutton_tab_bullets
            self.builder.get_object("checkbutton_tab_bullets").set_active(self.file.tab_bullets)
            #checkbutton_show_titles_in_view
            self.builder.get_object("checkbutton_show_titles_in_view").set_active(self.document.show_titles_in_view)
            #checkbutton_show_titles_in_export
            self.builder.get_object("checkbutton_show_titles_in_export").set_active(self.document.show_titles_in_export)
            #checkbutton_remember_position
            self.builder.get_object("checkbutton_remember_position").set_active(self.file.remember_position)
            #calculate_statistics
            self.builder.get_object("checkbutton_calculate_statistics").set_active(self.file.calculate_statistics)
            #show_application_name
            self.builder.get_object("checkbutton_show_application_name").set_active(self.file.show_application_name)
            #show_directory
            self.builder.get_object("checkbutton_show_directory").set_active(self.file.show_directory_status)
            #tree_toolbar_intree
            self.builder.get_object("checkbutton_tree_toolbar_intree").set_active(self.file.tree_toolbar_intree)
            #entry_max_tabs
            self.builder.get_object("spinbutton_max_tabs").set_value(self.document.tab_max)
            #entry_max_history
            self.builder.get_object("spinbutton_max_history").set_value(self.file.max_history)
            #entry_max_bookmarks
            self.builder.get_object("spinbutton_max_bookmarks").set_value(self.document.bookmark_max)
            #entry_max_visits
            self.builder.get_object("spinbutton_max_visits").set_value(self.document.visited_max)
            #entry_autosave_interval
            self.builder.get_object("spinbutton_autosave_interval").set_value(self.file.autosave_interval)
            #application_name
            self.builder.get_object("entry_application_name").set_text(self.file.application_name)
            #entry_spaces_above
            self.builder.get_object("spinbutton_spaces_above").set_value(self.file.spaces_above)
            #entry_spaces_below
            self.builder.get_object("spinbutton_spaces_below").set_value(self.file.spaces_below)
            self.populating = False

        # close
        def closed_button_callback(self, data=None):
            self.window.hide()

        #checkbutton_openlastfile
        def checkbutton_openlastfile_callback(self, toggled, data=None):
            menu_item = self.builder.get_object("checkbutton_openlastfile")
            self.file.autoopen = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_saveonexit
        def checkbutton_saveonexit_callback(self, toggled, data=None):
            menu_item = self.builder.get_object("checkbutton_saveonexit")
            self.file.save_on_exit = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_autosave
        def checkbutton_autosave_callback(self, toggled, data=None):
            menu_item = self.builder.get_object("checkbutton_autosave")
            self.file.autosave = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_autosave_version
        def checkbutton_autosave_version_callback(self, toggled, data=None):
            menu_item = self.builder.get_object("checkbutton_autosave_version")
            self.file.autosave_version = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_tooltext    
        def checkbutton_tooltext_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_tooltext")    
            self.file.tool_text = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_show_tabs
        def checkbutton_show_tabs_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_show_tabs")    
            self.file.show_tabs = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_node_path
        def checkbutton_node_path_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_node_path")    
            self.file.show_node_path = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()
            self.kabikaboo.update_node_path()

        #checkbutton_node_path_status
        def checkbutton_node_path_status_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_node_path_status")    
            self.file.show_node_path_status = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()
            self.kabikaboo.update_node_path()

        #checkbutton_homog_tabs
        def checkbutton_homog_tabs_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_homog_tabs")    
            self.file.homog_tabs = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_tab_arrows    
        def checkbutton_tab_arrows_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_tab_arrows")
            self.file.show_tab_arrows = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_show_bullets
        def checkbutton_show_bullets_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_show_bullets")
            self.file.show_bullets = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_attributes
        def checkbutton_attributes_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_attributes")
            self.file.show_attributes = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_settings()

        #checkbutton_file_status
        def checkbutton_file_status_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_file_status")    
            self.file.show_file_status = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_status_bar()

        #checkbutton_move_on_new
        def checkbutton_move_on_new_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_move_on_new")    
            self.file.move_on_new = menu_item.get_active()
            self.file.save_settings_default()

        #checkbutton_sample_data
        def checkbutton_sample_data_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_sample_data")
            self.file.sample_data = menu_item.get_active()
            self.file.save_settings_default()

        #checkbutton_tab_bullets
        def checkbutton_tab_bullets_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_tab_bullets")
            self.file.tab_bullets = menu_item.get_active()
            self.file.save_settings_default()
            self.kabikaboo.update_notebook()

        #checkbutton_show_titles_in_view
        def checkbutton_show_titles_in_view_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_show_titles_in_view")
            self.document.show_titles_in_view = menu_item.get_active()
            self.kabikaboo.update_textview()
            self.bump()

        #checkbutton_show_titles_in_export
        def checkbutton_show_titles_in_export_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_show_titles_in_export")
            self.document.show_titles_in_export = menu_item.get_active()
            self.bump()

        #checkbutton_remember_position
        def checkbutton_remember_position_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_remember_position")
            self.file.remember_position = menu_item.get_active()
            self.file.diff_set = False
            self.file.save_settings_default()

        #checkbutton_calculate_statistics
        def checkbutton_calculate_statistics_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_calculate_statistics")
            self.file.calculate_statistics = menu_item.get_active()
            self.file.save_settings_default()

        #checkbutton_show_application_name
        def checkbutton_show_application_name_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_show_application_name")
            self.file.show_application_name = menu_item.get_active()
            self.kabikaboo.update_window_titles()
            self.file.save_settings_default()

        #checkbutton_show_directory
        def checkbutton_show_directory_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_show_directory")
            self.file.show_directory_status = menu_item.get_active()
            self.kabikaboo.update_status_bar()
            self.file.save_settings_default()

        #checkbutton_tree_toolbar_intree
        def checkbutton_tree_toolbar_intree_callback(self, toggled, data=None): 
            menu_item = self.builder.get_object("checkbutton_tree_toolbar_intree")
            self.file.tree_toolbar_intree = menu_item.get_active()
            # we would call the next function, treebar_swap
            #  but it seems either GTK has a bug here, or we are missing something
            #  until this is resolved, the user has to exit and restart to see the change
            #self.kabikaboo.treebar_swap()
            self.file.save_settings_default()

        #entry_max_tabs
        def entry_max_tabs_callback(self, spinbutton, data=None):
            entry = self.builder.get_object("spinbutton_max_tabs")
            good_value = True
            try:
                tab_max = entry.get_value_as_int()
            except:
                tab_max = self.document.tab_max
                good_value = False
            if good_value and tab_max != self.document.tab_max:
                if(tab_max >= 1):
                    self.document.tab_max = tab_max
                    self.document.check_tab_overflow()
                    entry.set_value(self.document.tab_max)
                    self.kabikaboo.check_notebook()
                    self.bump()

        #entry_max_history
        def entry_max_history_callback(self, spinbutton, data=None):
            entry = self.builder.get_object("spinbutton_max_history")
            good_value = True
            try:
                max_history = entry.get_value_as_int()
            except:
                max_history = self.file.max_history
                good_value = False
            if good_value and max_history != self.file.max_history:
                if(max_history >= 1):
                    self.file.max_history = max_history
                entry.set_value(self.file.max_history)
                self.file.check_history()
                self.kabikaboo.update_history()
                self.file.save_settings_default()

        #entry_max_bookmarks
        def entry_max_bookmarks_callback(self, spinbutton, data=None):
            entry = self.builder.get_object("spinbutton_max_bookmarks")
            good_value = True
            try:
                bookmark_max = entry.get_value_as_int()
            except:
                bookmark_max = self.document.bookmark_max
                good_value = False
            if good_value and bookmark_max != self.document.bookmark_max:
                if(bookmark_max >= 1):
                    self.document.bookmark_max = bookmark_max
                    self.document.check_bookmark_overflow()
                    entry.set_value(self.document.bookmark_max)
                    self.kabikaboo.update_bookmarks()
                    self.bump()

        #entry_max_visits
        def entry_max_visits_callback(self, spinbutton, data=None):
            entry = self.builder.get_object("spinbutton_max_visits")
            good_value = True
            try:
                visited_max = entry.get_value_as_int()
            except:
                visited_max = self.document.visited_max
                good_value = False
            if good_value and visited_max != self.document.visited_max:
                if(visited_max >= 1):
                    self.document.visited_max = visited_max
                    self.document.check_visited_overflow()
                    entry.set_value(self.document.visited_max)
                    self.bump()

        #entry_autosave_interval
        def entry_autosave_interval_callback(self, spinbutton, data=None):
            entry = self.builder.get_object("spinbutton_autosave_interval")
            good_value = True
            try:
                autosave_interval = entry.get_value_as_int()
            except:
                autosave_interval = self.file.autosave_interval
                good_value = False
            if good_value and autosave_interval != self.file.autosave_interval:
                if(autosave_interval >= 1):
                    self.file.autosave_interval = autosave_interval
                    entry.set_value(self.file.autosave_interval)
                    self.kabikaboo.check_autosave()
       
       #entry_spaces_above
        def entry_spaces_above_callback(self, spinbutton, data=None):
            entry = self.builder.get_object("spinbutton_spaces_above")
            good_value = True
            try:
                spaces_above = entry.get_value_as_int()
            except:
                spaces_above = self.file.autosave_interval
                good_value = False
            if good_value and spaces_above != self.file.spaces_above:
                if(spaces_above >= 1):
                    self.file.spaces_above = spaces_above
                    entry.set_value(self.file.spaces_above)
                    self.kabikaboo.check_spaces_above()
       
       #entry_spaces_below
        def entry_spaces_below_callback(self, spinbutton, data=None):
            entry = self.builder.get_object("spinbutton_spaces_below")
            good_value = True
            try:
                spaces_below = entry.get_value_as_int()
            except:
                spaces_below = self.file.autosave_interval
                good_value = False
            if good_value and spaces_below != self.file.spaces_below:
                if(spaces_below >= 1):
                    self.file.spaces_below = spaces_below
                    entry.set_value(self.file.spaces_below)
                    self.kabikaboo.check_spaces_below()
       
       
    #entry_application_name
    def entry_application_name_callback(self, entrybox, data=None): 
        entry = self.builder.get_object("entry_application_name")
        application_name = entry.get_text()
        if self.file.application_name != application_name:
            self.file.application_name = application_name
            self.kabikaboo.update_window_titles()
            self.file.save_settings_default()

    # mark the document as changed 
    def bump(self):
        if not self.populating:
            self.kabikaboo.bump()
