#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Kabikaboo
#
# Recursive Writing Assistance Software
# Created by 
#  David Glen Kerr
#  Jeremy Bicha
#
# Licensed under GPL v2 or later
# Free and Open Source
# Copyleft (c) 2009
# No Warranty

# Import Kabikaboo codebase
from document import *
from file import *
from settings import *
from statistics import *
# external imports
import commands
import os
import string
import sys
import time
# dependency: apt-get install python-gtk2
import gobject
import gtk
import pango
import pygtk
# dependency: apt-get install python-gtksourceview2
import gtksourceview2
# dependency: apt-get install python-gtkspell
import gtkspell
# dependency : apt-get install python-gnome2
import gnome

# KabikabooMainWindow
#
# Special thanks to Flint James Kerr
#  creator of the explosion sound "kabik-kaboo!"
#
class KabikabooMainWindow:
    # Init Step 1: init main window
    def __init__(self):
        # create document holder
        self.document = KabikabooDocument()
        # create file handler
        self.file = KabikabooFile()

    # Init Step 2: initialize gui interface
    def initialize_interface(self):
        # buffer
        self.copying_buffer = True
        # tell it we are positioning the window
        self.positioning = True
        # create window
        self.build_window()
        # find components in window
        self.find_window_components()
        # check for duplicate instance of kabikaboo
        if not self.check_for_duplicate_instance():
            # open last file
            self.open_file_on_startup()
        # initialize variables
        self.initialize_variables()
        # create notebook
        self.create_notebook()
        # create treeview
        self.create_treeview()
        # size up component sizes
        self.set_gui_sizes()
        # application icon
        self.load_application_icon()
        # connect signals
        self.builder.connect_signals(self)
        # tree toolbar
        self.create_toolbar_tree()
        # text toolbar
        self.create_toolbar_text()
        # update the status bar
        self.update_status_bar()
        # menu items
        self.create_menu_items()
        # attributes callbacks
        self.connect_attributes_panel()
        # history
        self.create_history_gui()
        # bookmarks
        self.create_bookmarks_gui()
        # visited
        self.create_visited_gui()
        # autosave
        self.autosave_id = -1
        self.check_autosave()
        # keep open
        self.keep_open = True
        # done positioning window
        self.positioning = False

    # Init Step 3: populate gui interface
    def populate_interface(self):
        # update everything
        self.set_window_title()
        self.match_tree_to_document()
        self.refresh_tree()
        self.update_status_bar()
        self.apply_settings()
        self.match_notebook_to_document()
        self.update_tool_buttons()
        self.update_settings_window()
        self.update_history()
        self.update_bookmarks()
        # save these for post_window_show():
        #self.update_attributes()
        #self.update_node_path()

    # Init Step 4: show the window
    def window_show(self):
        self.window.show()

    # Init Step 5: do after the window is shown
    def post_window_show(self):
        # position window
        if self.file.remember_position and not self.file.window_maximized:
            if self.file.window_x != -1 and self.file.window_y != -1:
                self.positioning = True
                self.window.set_position(gtk.WIN_POS_NONE)
                self.window.move(self.file.window_x - self.file.diff_x, self.file.window_y - self.file.diff_y)
                self.positioning = False
        if self.file.fullscreen:
            self.window.fullscreen()
        self.open_first_notebook_tab()
        # need to update these because they get offcentered
        self.update_node_path()
        self.update_attributes()

    # one-time call to set up variables and pointers
    def initialize_variables(self):
        # find text view
        self.current_textview = None
        # search result
        self.found = None
        # keep a reference to the viewd textview, its handy
        self.current_textview = None
        # keep a reference to the viewd buffer, its handy
        self.current_buffer = None
        # create a reference to editing iterator
        self.editor_iter = None
        # create a reference to editing node
        self.editor_node = None
        # pages
        self.current_page = None
        self.last_page = None
        # internal flags
        self.updating_attributes = False
        self.changing_cursor = False
        self.switching_page = False
        # settings window init
        self.settings = None
        # statistics window
        self.statistics = None
        # calculate statistics on startup?
        self.start_time = time.time()
        self.start_word_count = -1
        if self.file.calculate_statistics:
            self.start_word_count = self.document.word_count()

    # one time call to build the window
    def build_window(self):
        # create gtk builder
        self.builder = gtk.Builder()
        # load interface
        if os.path.isfile(os.path.join("ui", "main.glade")):
            self.builder.add_from_file(os.path.join("ui", "main.glade"))
        elif os.path.isfile(os.path.join("..", "ui", "main.glade")):
            self.builder.add_from_file(os.path.join("..", "ui", "main.glade"))
        elif os.path.isfile("/usr/share/kabikaboo/ui/main.glade"):
            self.builder.add_from_file("/usr/share/kabikaboo/ui/main.glade")

        # find main window
        self.window = self.builder.get_object("window_main")
        # window callbacks
        self.window.connect("delete-event", self.on_window_delete)
        self.window.connect("key-press-event", self.window_key_press_callback)
        self.window.connect('window-state-event', self.on_window_state_change)
        self.window.connect('size-allocate', self.on_window_size_allocate)
        self.window.connect('configure-event', self.on_window_move)


    # one time call to store pointers of window components
    def find_window_components(self):
        # store main horizontal panel splitter
        self.hpaned_main = self.builder.get_object("hpaned_main")
        # store left vertical panel splitter
        self.vpaned_left = self.builder.get_object("vpaned_left")
        # store attributes bullet area
        self.fixed_node_bullet = self.builder.get_object("fixed_node_bullet")
        # remember some labels
        self.label_title = self.builder.get_object("label_title")
        self.label_status_filename = self.builder.get_object("label_status_filename")
        self.label_node_path = self.builder.get_object("label_node_path")
        # grab status bar
        self.statusbar = self.builder.get_object("statusbar")
        # fixed attributes box
        self.attributes_area = self.builder.get_object("vpaned_attributes")
        # main menu
        self.main_menu = self.builder.get_object("menubar")
        self.menu_action_group = self.builder.get_object("actiongroup_menu")

    # one time call to create the treeview
    def create_treeview(self):
        # find tree
        self.treeview = self.builder.get_object("treeview")
        self.treeview.connect("key-press-event", self.treeview_key_press_callback)
        self.treeview.connect("button-press-event", self.treeview_button_press_callback)
        # create a treestore to hold the title and id data
        self.treestore = gtk.TreeStore(str, int)
        self.treeview.set_model(self.treestore)
        # create a visual expander column for titles
        self.treecolumn = gtk.TreeViewColumn('Titles')
        self.treeview.append_column(self.treecolumn)
        # hide the header, we dont need to see it
        self.treeview.set_headers_visible(False)
        # show tree lines - looks nice
        self.treeview.set_property('enable-tree-lines', True)
        # dont allow user to drag and drop tree nodes yet
        self.treeview.set_property('reorderable', False)
        # create a cell renderer to display title text on tree nodes
        self.cell = gtk.CellRendererText()
        self.cell.set_property('editable', True)
        self.cell.connect('edited', self.cell_changed_callback)
        # not sure what pack_start does
        self.treecolumn.pack_start(self.cell, True)
        # not sure what this does
        self.treecolumn.add_attribute(self.cell, 'text', 0)
        # when the user picks a new tree node, call this
        self.treeview.connect("cursor-changed", self.cursor_changed_callback)

    # one time call to create the notebook
    def create_notebook(self):
        # note book
        self.notebook = self.builder.get_object("notebook_tabs")
        # note book tabs list of node pointers
        self.book_node_ids = []
        # note book tabs list of iter pointers
        self.book_iters = []
        # note book tab textviews (one on each page)
        self.book_textviews = []
        self.book_page = -1
        # tabbed book node id list
        self.book_node_ids = []
        # note book tabs list of iter pointers
        self.book_iters = []
        # note book tab textviews (one on each page)
        self.book_textviews = []
        # no page selected yet
        self.book_page = -1
        # get the notebook
        self.notebook.set_scrollable(True)
        self.notebook.set_property('enable-popup', True)
        self.notebook.connect("switch-page", self.notebook_switch_page_callback)

    # set sizes
    def set_gui_sizes(self):
        # resize window
        self.window.set_default_size(self.file.window_width, self.file.window_height)
        # maximize
        if self.file.window_maximized:
            self.window.maximize()
        # resize treeview
        if self.file.tree_width > -1:
            self.hpaned_main.set_position(self.file.tree_width)
        # set vertical panel
        if self.file.attribute_panel_height > -1:
            self.vpaned_left.set_position(self.file.window_height - self.file.attribute_panel_height)
        # resize node title
        self.label_title.set_property("width-request", self.hpaned_main.get_position())

    # destroy window action
    def on_window_main_destroy(self, widget, data=None):
        if self.keep_open:
            self.keep_open = self.close_window_query()
        if not self.keep_open:
            self.file.tree_width = self.hpaned_main.get_position()
            self.file.attribute_panel_height = self.file.window_height - self.vpaned_left.get_position()
            self.file.close(self.document)
            gtk.main_quit()

    # destroy window action
    def on_window_delete(self, widget, data=None):
        self.keep_open = self.close_window_query()
        return self.keep_open
        
    # ok to delete query
    def close_window_query(self):
        if self.file.different and not self.file.save_on_exit and self.file.working_file!='':
            dialog = gtk.MessageDialog(self.window, 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_INFO, 
                gtk.BUTTONS_YES_NO, 
                "Your changes are not saved.\nQuit anyways?")
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_NO:
                return True
            else:
                return False
        else:
            return False

    # set the title of the window
    def set_window_title(self):
        title = self.document.title
        if self.file.show_application_name and self.file.application_name != '':
            title = self.file.application_name
            if self.document.title != self.file.application_name:
                title = self.document.title + ' - ' + self.file.application_name
        if self.file.different:
            title = '*' + title
        self.window.set_title(title)
        if self.statistics:
            self.statistics.update_title()

    # update titles on all windows
    def update_window_titles(self):
        self.set_window_title()
        if self.settings:
            self.settings.set_window_title()
        if self.statistics:
            self.statistics.set_window_title()

    # populate the status bar
    def update_status_bar(self, message=''):
        self.label_status_filename.set_label('')
        status = ''
        if self.file.show_file_status:
            if self.file.working_file != '':
                if self.file.show_directory_status:
                    status = self.file.working_file + ' '
                else:
                    status = os.path.basename(self.file.working_file) + ' '
            else:
                status = 'New Document '
        if self.file.different:
            status = status + '(changed)'
        if message:
            status = status + ' - ' + message
        self.label_status_filename.set_label(status)

    # load and set the application icon
    def load_application_icon(self):
        if os.path.isfile("kabikaboo.png"):
            gtk.window_set_default_icon_from_file("kabikaboo.png")
        elif os.path.isfile(os.path.join("..", "kabikaboo.png")):
            gtk.window_set_default_icon_from_file(os.path.join("..", "kabikaboo.png"))
        elif os.path.isfile("/usr/src/kabikaboo/kabikaboo.png"):
            gtk.window.set_default_icon_from_file("/usr/src/kabikaboo/kabikaboo.png")
        elif os.path.isfile("/usr/share/kabikaboo/kabikaboo.png"):
         self.window.set_icon_from_file("/usr/share/kabikaboo/kabikaboo.png")

    # detect some keys
    def window_key_press_callback(self, window, event, data=None):
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        mod = gtk.accelerator_get_label(keyval,event.state)
        #print '%s - %d' % (mod, keyval)
        # on some systems it adds Mod2+ into the string
        mod = string.replace(mod, 'Mod2+', '')
        # ctrl+tab
        if mod == 'Ctrl+Tab':
            self.next_notebook_page()
            self.notebook.grab_focus()
        # shift+ctrl+tab
        elif mod == 'Shift+Ctrl+ISO Left Tab' or mod == 'Shift+Ctrl+ISO Right Tab':
            self.previous_notebook_page()
            self.notebook.grab_focus()
        # alt+home
        elif mod == 'Alt+Home':
            self.default_view()
            self.treeview.grab_focus()
        # F2 (edit node title)
        elif mod == 'F2':
            self.edit_node_title()

    # detect textview keys
    def textview_key_press_callback(self, window, event, data=None):
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        mod = gtk.accelerator_get_label(keyval,event.state)
        #print '%s - %d' % (mod, keyval)
        # on some systems it adds Mod2+ into the string
        mod = string.replace(mod, 'Mod2+', '')
        # Ctrl+W (close tab)
        if mod == 'Ctrl+W':
            self.close_current_notebook_page()
        '''# italic
        elif mod == 'Ctrl+I':
            self.italic_callback(window)
        # bold
        elif mod == 'Ctrl+B':
            self.bold_callback(window)
        # underline
        elif mod == 'Ctrl+U':
            self.underline_callback(window)'''

    # detect treeview keys
    def treeview_key_press_callback(self, window, event, data=None):
        keyval = event.keyval
        name = gtk.gdk.keyval_name(keyval)
        mod = gtk.accelerator_get_label(keyval,event.state)
        #print '%s - %d' % (mod, keyval)
        # on some systems it adds Mod2+ into the string
        mod = string.replace(mod, 'Mod2+', '')
        # delete (delete node)
        if mod == 'Delete':
            self.remove_node_callback()
        # ctrl+delete (delete children)
        elif mod == 'Ctrl+Delete':
            self.remove_children_callback()
        # ctrl+up (move up)
        elif mod == 'Ctrl+Up':
            self.move_node_up_callback()
        # ctrl+down (move down)
        elif mod == 'Ctrl+Down':
            self.move_node_down_callback()
        # ctrl+left (move left)
        elif mod == 'Ctrl+Left':
            self.move_node_left_callback()
        # ctrl+right (move right)
        elif mod == 'Ctrl+Right':
            self.move_node_right_callback()
        # ctrl+e (edit node)
        elif mod == 'Ctrl+E':
            self.set_node_edit()
        # ctrl+v (view node)
        elif mod == 'Ctrl+V':
            self.set_node_view()
        # ctrl+g (view grandchildren)
        elif mod == 'Ctrl+G':
            self.flip_node_grandchildren()
        # ctrl+b (add before)
        elif mod == 'Ctrl+B':
            self.new_node_before_callback()   
        # ctrl+a (add after)
        elif mod == 'Ctrl+A':
            self.new_node_after_callback()   
        # ctrl+c (add child)
        elif mod == 'Ctrl+C':
            self.new_child_node_callback()   
        # right (expand)
        elif mod == 'Right':
            self.expand_row_callback()
        # left (collapse)
        elif mod == 'Left':
            self.collapse_row_callback()
        # ctrl++ (expand children)
        elif mod == 'Ctrl+=' or mod == 'Ctrl+X':
            self.expand_all_children_callback()         
        # home (delete children)
        elif mod == 'Home':
            self.default_view()
        # F2 (edit node title)
        elif mod == 'F2':
            self.edit_node_title()

    # callback for changed text in textview
    def text_changed_callback(self, textbuffer, data=None):
        # do we have a node selected?
        if self.editor_node and self.editor_iter and not self.editor_node.view:
            if not self.copying_buffer:
                # store the text from textview's buffer into our document
                text = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter())
                self.editor_node.set_text(text)
                self.bump()

    # callback for user beginning to edit a row of treeview
    # note: doesnt work, gtk stops us from modifying the cell
    def cell_editing_callback(self, cell, editable, path, data=None):
        # do we have a node selected?
        if self.editor_node and self.editor_iter:
            self.treestore.set(self.editor_iter, 0, self.editor_node.title)

    # callback for user editing row of treeview
    def cell_changed_callback(self, cell, path, new_text, data=None):
        # do we have a node selected?
        if self.editor_node and self.editor_iter:
            # compare new text with bulleting
            bullet = self.editor_node.get_title_bullet()
            if len(bullet) > 0:
                if new_text[0:len(bullet)] == bullet:
                    # strip out the bulleting
                    new_text = new_text[len(bullet):len(new_text)]
            # store the new cell title into our document
            if new_text != self.editor_node.title:
                self.editor_node.title = new_text
                # also update the visual treeview with the new title
                self.treestore.set_value(self.editor_iter, 0, self.editor_node.get_title())
                # check if this is the document
                if self.editor_node == self.document:
                    self.set_window_title()
                if self.editor_node.view:
                    self.update_textview_safe()
                self.update_node_path()
                self.update_notebook()
                self.update_bookmarks()
                self.update_attributes()
                self.bump()

    # callback for user selecting row of treeview
    def cursor_changed_callback(self, treeview, data=None):
        if not self.changing_cursor:
            # grab the selection
            selection = treeview.get_selection()
            # get the iterator from the selection
            (model, iter) = selection.get_selected()
            if iter:
                # grab the id from the second column
                id = self.treestore.get_value(iter, 1)
                # find the node in our document matching this id
                node = self.document.fetch_node_by_id(id)
                if node:
                    # store the currently selected iterator and node
                    self.editor_iter = iter
                    self.editor_node = node
                    # copy the document's node text to the textview buffer
                    self.add_to_notebook(node, iter)
                    self.update_textview()
                    self.node_visit(node)
                else:
                    self.editor_node = None
                    self.editor_iter = None
                    self.set_textbuffer('')
            else:
                self.editor_node = None
                self.editor_iter = None
                self.set_textbuffer('')
            self.update_node_path()
            self.update_attributes()
            self.update_tool_buttons()

    # update the node path label
    # using statusbar.pop instead of a simpler, more powerful label because I can't
    # figure out how to get a label to display the long names common for node paths
    def update_node_path(self):
        # top node path
        if self.file.show_node_path:
            if self.book_page >= 0 and self.editor_node:
                self.label_node_path.set_label('<small><tt>'+self.editor_node.get_recursive_title()+'</tt></small>')
            else:
                self.label_node_path.set_label('')
            self.label_node_path.set_property('visible', True)
        else:
            self.label_node_path.set_property('visible', False)
        # bottom node path in status bar
        if self.file.show_node_path_status:
            self.statusbar.pop(0)
            status = ''
            if self.book_page >= 0 and self.editor_node:
                status = '  ' + self.editor_node.get_recursive_title()
        else:
            status = ''
        self.statusbar.push(0, status)

    # update the text in the textview
    def update_textview(self):
        if self.current_textview:
            if self.editor_node and self.editor_iter:
                if not self.editor_node.view:
                    noundo = False
                    if len(self.current_buffer.get_text(self.current_buffer.get_start_iter(), self.current_buffer.get_end_iter())) == 0:
                        noundo = True
                    if noundo:
                        self.current_buffer.begin_not_undoable_action()
                    self.set_textbuffer(self.editor_node.get_text())
                    if noundo:
                        self.current_buffer.end_not_undoable_action()
                    self.current_textview.set_editable(True)
                    self.current_textview.set_cursor_visible(True)
                else:
                    #self.current_buffer.set_property("redo", False)
                    #self.current_buffer.set_property("canundo", False)
                    self.current_buffer.begin_not_undoable_action()
                    self.fancy_text(self.editor_node)
                    self.current_buffer.end_not_undoable_action()
                    self.current_textview.set_editable(False)
                    self.current_textview.set_cursor_visible(False)
            else:
                self.current_buffer.begin_not_undoable_action()
                self.set_textbuffer('')
                self.current_buffer.end_not_undoable_action()
                self.current_textview.set_editable(False)
                self.current_textview.set_cursor_visible(False)

    # update the text in the textview (only if it is a view node)
    def update_textview_safe(self):
        if self.current_textview:
            if self.editor_node and self.editor_iter:
                if self.editor_node.view:
                    noundo = False
                    if len(self.current_buffer.get_text(self.current_buffer.get_start_iter(), self.current_buffer.get_end_iter())) == 0:
                        noundo = True
                    if noundo:
                        self.current_buffer.begin_not_undoable_action()
                    self.fancy_text(self.editor_node)
                    if noundo:
                        self.current_buffer.end_not_undoable_action()
                    self.current_textview.set_editable(False)
                    self.current_textview.set_cursor_visible(False)
                if not self.editor_node.view:
                    self.current_textview.set_editable(True)
                    self.current_textview.set_cursor_visible(True)
                else:
                    self.current_textview.set_editable(False)
                    self.current_textview.set_cursor_visible(False)
            else:
                self.current_buffer.begin_not_undoable_action()
                self.set_textbuffer('')
                self.current_buffer.end_not_undoable_action()
                self.current_textview.set_editable(False)
                self.current_textview.set_cursor_visible(False)

    # tree toolbar init
    def create_toolbar_tree(self):
        self.toolbar_tree = self.builder.get_object("toolbar_tree")
        self.toolbutton_default_view = self.builder.get_object("toolbutton_default_view")
        self.toolbutton_default_view.connect('clicked', self.default_view_callback)
        # separator
        self.toolbutton_sep2 = self.builder.get_object("toolbutton_sep2")
        # add child toolbutton
        self.toolbutton_add_child = self.builder.get_object("toolbutton_add_child")
        self.toolbutton_add_child.connect('clicked', self.new_child_node_callback)
        # add before toolbutton
        self.toolbutton_add_before = self.builder.get_object("toolbutton_add_before")
        self.toolbutton_add_before.connect('clicked', self.new_node_before_callback)
        # add after toolbutton
        self.toolbutton_add_after = self.builder.get_object("toolbutton_add_after")
        self.toolbutton_add_after.connect('clicked', self.new_node_after_callback)
        # separator
        self.toolbutton_sep3 = self.builder.get_object("toolbutton_sep3")
        # move up toolbutton
        self.toolbutton_move_up = self.builder.get_object("toolbutton_move_up")
        self.toolbutton_move_up.connect('clicked', self.move_node_up_callback)
        # move down toolbutton
        self.toolbutton_move_down = self.builder.get_object("toolbutton_move_down")
        self.toolbutton_move_down.connect('clicked', self.move_node_down_callback)
        # move left toolbutton
        self.toolbutton_move_left = self.builder.get_object("toolbutton_move_left")
        self.toolbutton_move_left.connect('clicked', self.move_node_left_callback)
        # move right toolbutton
        self.toolbutton_move_right = self.builder.get_object("toolbutton_move_right")
        self.toolbutton_move_right.connect('clicked', self.move_node_right_callback)
        # expand toolbutton
        self.toolbutton_expand = self.builder.get_object("toolbutton_expand")
        self.toolbutton_expand.connect('clicked', self.expand_row_callback)
        # expand children toolbutton
        self.toolbutton_expand_children = self.builder.get_object("toolbutton_expand_children")
        self.toolbutton_expand_children.connect('clicked', self.expand_all_children_callback)
        # collapse toolbutton
        self.toolbutton_collapse = self.builder.get_object("toolbutton_collapse")
        self.toolbutton_collapse.connect('clicked', self.collapse_row_callback)
        # remove toolbutton
        self.toolbutton_remove = self.builder.get_object("toolbutton_remove")
        self.toolbutton_remove.connect('clicked', self.remove_node_callback)
        # remove children toolbutton
        self.toolbutton_remove_children = self.builder.get_object("toolbutton_remove_children")
        self.toolbutton_remove_children.connect('clicked', self.remove_children_callback)
        # move the tree toolbar?
        if self.file.tree_toolbar_intree: #default is out of tree
            self.treebar_swap()

    # place the treebar in one of two places
    # BUG: requires restart when called from settings because buttons stop working
    #      works fine from application startup tho...
    def treebar_swap(self):
        if self.file.tree_toolbar_intree:
            # in with the tree
            vbox_tree = self.builder.get_object("vbox_tree")
            self.toolbar_tree.hide()
            self.toolbar_tree.reparent(vbox_tree)
            vbox_tree.reorder_child(self.toolbar_tree, 0)
            vbox_tree.set_child_packing(self.toolbar_tree, False, False, 0, gtk.PACK_START)
            self.toolbar_tree.show()
        else:
            # up across top
            self.toolbar_tree.hide()
            hpaned_toolbar = self.builder.get_object("hpaned_toolbar")
            self.toolbar_tree.reparent(hpaned_toolbar)
            self.toolbar_tree.show()

    # set whether the tool buttons are enabled or not
    def update_tool_buttons(self):
        # later, we can add a settings option to customize these:
        tool_enabled = "visible" # TODO: user may want sensitive or visible here
        menu_enabled = "sensitive"
        # enable/disable buttons
        # NOTHING SELECTED
        if not self.editor_node or not self.editor_iter:
            self.toolbutton_expand.set_property(tool_enabled, False)
            self.toolbutton_collapse.set_property(tool_enabled, False)
            self.toolbutton_expand_children.set_property(tool_enabled, False)
            self.toolbutton_add_child.set_property(tool_enabled, False)
            self.toolbutton_add_after.set_property(tool_enabled, False)
            self.toolbutton_add_before.set_property(tool_enabled, False)
            self.toolbutton_remove.set_property(tool_enabled, False)
            self.toolbutton_remove_children.set_property(tool_enabled, False)
            self.toolbutton_move_up.set_property(tool_enabled, False)
            self.toolbutton_move_down.set_property(tool_enabled, False)
            self.toolbutton_move_left.set_property(tool_enabled, False)
            self.toolbutton_move_right.set_property(tool_enabled, False)
            self.toolbutton_sep2.set_property(tool_enabled, False)
            self.toolbutton_sep3.set_property(tool_enabled, False)
            self.export_node_menu_item.set_property(menu_enabled, False)
            self.export_node_children_menu_item.set_property(menu_enabled, False)
            self.export_html_node_menu_item.set_property(menu_enabled, False)
            self.export_html_node_children_menu_item.set_property(menu_enabled, False)
            self.import_text_menu_item.set_property(menu_enabled, False)
            self.split_one_menu_item.set_property(menu_enabled, False)
            self.split_two_menu_item.set_property(menu_enabled, False)
            self.unify_with_menu_item.set_property(menu_enabled, False)
            self.unify_without_menu_item.set_property(menu_enabled, False)
            self.toolbar_text.set_property('visible', False)
            self.undo_menu_item.set_property(menu_enabled, False)
            self.redo_menu_item.set_property(menu_enabled, False)
            self.cut_menu_item.set_property(menu_enabled, False)
            self.copy_menu_item.set_property(menu_enabled, False)
            self.paste_menu_item.set_property(menu_enabled, False)
        # NODE SELECTED
        else: # we have a node selected
            # DOCUMENT ROOT NODE SELECTED
            if self.editor_node == self.document: # main document node is selected
                self.export_node_menu_item.set_property(menu_enabled, False)
                self.export_node_children_menu_item.set_property(menu_enabled, False)
                self.export_html_node_menu_item.set_property(menu_enabled, False)
                self.export_html_node_children_menu_item.set_property(menu_enabled, False)
                self.toolbutton_expand.set_property(tool_enabled, True)
                self.toolbutton_collapse.set_property(tool_enabled, True)
                self.toolbutton_expand_children.set_property(tool_enabled, True)
                self.toolbutton_add_child.set_property(tool_enabled, True)
                self.toolbutton_add_after.set_property(tool_enabled, False)
                self.toolbutton_add_before.set_property(tool_enabled, False)
                self.toolbutton_remove.set_property(tool_enabled, False)
                self.toolbutton_remove_children.set_property(tool_enabled, self.editor_node.has_children())
                self.toolbutton_move_up.set_property(tool_enabled, False)
                self.toolbutton_move_down.set_property(tool_enabled, False)
                self.toolbutton_move_left.set_property(tool_enabled, False)
                self.toolbutton_move_right.set_property(tool_enabled, False)
                self.toolbutton_sep2.set_property(tool_enabled, False)
                self.toolbutton_sep3.set_property(tool_enabled, True)
                self.import_text_menu_item.set_property(menu_enabled, True)
                self.split_one_menu_item.set_property(menu_enabled, self.editor_node.is_splittable())
                self.split_two_menu_item.set_property(menu_enabled, self.editor_node.is_splittable())
                self.unify_with_menu_item.set_property(menu_enabled, self.editor_node.is_unifiable())
                self.unify_without_menu_item.set_property(menu_enabled, self.editor_node.is_unifiable())
            # CHILD NODE SELECTED
            else: # a child node of the document is selected
                self.export_node_menu_item.set_property(menu_enabled, True)
                self.export_node_children_menu_item.set_property(menu_enabled, self.editor_node.has_children())
                self.export_html_node_menu_item.set_property(menu_enabled, True)
                self.export_html_node_children_menu_item.set_property(menu_enabled, self.editor_node.has_children())
                self.split_one_menu_item.set_property(menu_enabled, self.editor_node.is_splittable())
                self.split_two_menu_item.set_property(menu_enabled, self.editor_node.is_splittable())
                self.unify_with_menu_item.set_property(menu_enabled, self.editor_node.is_unifiable())
                self.unify_without_menu_item.set_property(menu_enabled, self.editor_node.is_unifiable())
                # expand button
                self.toolbutton_expand.set_property(tool_enabled, self.editor_node.has_children())
                # collapse button
                self.toolbutton_collapse.set_property(tool_enabled, self.editor_node.has_children())
                # show all children button
                self.toolbutton_expand_children.set_property(tool_enabled, self.editor_node.has_children())
                self.toolbutton_add_child.set_property(tool_enabled, True)
                self.toolbutton_add_after.set_property(tool_enabled, True)
                self.toolbutton_add_before.set_property(tool_enabled, True)
                self.toolbutton_remove.set_property(tool_enabled, True)
                # remove children button
                self.toolbutton_remove_children.set_property(tool_enabled, self.editor_node.has_children())
                # move up button
                self.toolbutton_move_up.set_property(tool_enabled, not self.document.is_a_first_node(self.editor_node))
                # move down button
                self.toolbutton_move_down.set_property(tool_enabled, not self.document.is_a_last_node(self.editor_node))
                # move left button
                self.toolbutton_move_left.set_property(tool_enabled, self.document.can_move_left(self.editor_node))
                # move right button
                self.toolbutton_move_right.set_property(tool_enabled, self.document.can_move_right(self.editor_node))
                self.import_text_menu_item.set_property(menu_enabled, True)
                self.toolbutton_sep2.set_property(tool_enabled, True)
                self.toolbutton_sep3.set_property(tool_enabled, False)
            # ANY TYPE OF NODE
            # text tool bar
            if not self.editor_node.view and self.file.show_toolbar_text:
                self.toolbar_text.set_property('visible', True)
            else:
                self.toolbar_text.set_property('visible', False)
            # cut n paste etc
            self.undo_menu_item.set_property(menu_enabled, not self.editor_node.view)
            self.redo_menu_item.set_property(menu_enabled, not self.editor_node.view)
            self.cut_menu_item.set_property(menu_enabled, not self.editor_node.view)
            self.copy_menu_item.set_property(menu_enabled, not self.editor_node.view)
            self.paste_menu_item.set_property(menu_enabled, not self.editor_node.view)
        # notebook related buttons
        if len(self.book_node_ids) > 0:
            self.close_current_notebook_page_menu_item.set_property(menu_enabled, True)
            self.add_bookmark_menu_item.set_property(menu_enabled, not self.is_current_tab_a_bookmark())
            self.remove_bookmark_menu_item.set_property(menu_enabled, self.is_current_tab_a_bookmark())
        else:
            self.close_current_notebook_page_menu_item.set_property(menu_enabled, False)
            self.add_bookmark_menu_item.set_property(menu_enabled, False)
            self.remove_bookmark_menu_item.set_property(menu_enabled, False)
        self.toolbar_tree.queue_draw()

    # top menu init
    def create_menu_items(self):
        menu_item = self.builder.get_object("imagemenuitem_new")
        menu_item.connect("activate", self.new_document_callback)
        menu_item = self.builder.get_object("imagemenuitem_open")
        menu_item.connect("activate", self.open_document_callback)
        menu_item = self.builder.get_object("imagemenuitem_save")
        menu_item.connect("activate", self.save_document_callback)
        menu_item = self.builder.get_object("imagemenuitem_saveas")
        menu_item.connect("activate", self.save_as_document_callback)
        menu_item = self.builder.get_object("menuitem_save_copy")
        menu_item.connect("activate", self.save_copy_callback)
        menu_item = self.builder.get_object("menuitem_save_version")
        menu_item.connect("activate", self.save_version_callback)
        menu_item = self.builder.get_object("imagemenuitem_quit")
        menu_item.connect("activate", self.on_window_main_destroy)
        self.undo_menu_item = self.builder.get_object("imagemenuitem_undo")
        self.undo_menu_item.connect("activate", self.undo_callback)
        self.redo_menu_item = self.builder.get_object("imagemenuitem_redo")
        self.redo_menu_item.connect("activate", self.redo_callback)
        self.cut_menu_item = self.builder.get_object("imagemenuitem_cut")
        self.cut_menu_item.connect("activate", self.cut_callback)
        self.copy_menu_item = self.builder.get_object("imagemenuitem_copy")
        self.copy_menu_item.connect("activate", self.copy_callback)
        self.paste_menu_item = self.builder.get_object("imagemenuitem_paste")
        self.paste_menu_item.connect("activate", self.paste_callback)
        menu_item = self.builder.get_object("imagemenuitem_fullscreen")
        menu_item.connect("activate", self.fullscreen_switch)
        self.show_statusbar_menu_item = self.builder.get_object("checkmenuitem_statusbar")
        self.show_statusbar_menu_item.connect("toggled", self.show_statusbar_callback)
        self.show_toolbar_tree_menu_item = self.builder.get_object("checkmenuitem_toolbar_tree")
        self.show_toolbar_tree_menu_item.connect("toggled", self.show_toolbar_tree_callback)    
        menu_item = self.builder.get_object("checkmenuitem_toolbar_text")
        menu_item.connect("toggled", self.show_toolbar_text_callback)  
        self.show_attributes_menu_item = self.builder.get_object("checkmenuitem_show_attributes")
        self.show_attributes_menu_item.connect("toggled", self.show_attributes_callback)  
        menu_item = self.builder.get_object("checkmenuitem_spellcheck")
        menu_item.connect("toggled", self.checkbutton_spellcheck_callback)
        menu_item = self.builder.get_object("imagemenuitem_help")
        menu_item.connect("activate", self.help_callback)
        menu_item = self.builder.get_object("imagemenuitem_help_online")
        menu_item.connect("activate", lambda *a: gtk.show_uri(None, "http://answers.launchpad.net/kabikaboo", gtk.gdk.CURRENT_TIME))
        menu_item = self.builder.get_object("imagemenuitem_translate")
        menu_item.connect("activate", lambda *a: gtk.show_uri(None, "https://translations.launchpad.net/kabikaboo", gtk.gdk.CURRENT_TIME))
        menu_item = self.builder.get_object("imagemenuitem_report_problem")
        menu_item.connect("activate", lambda *a: gtk.show_uri(None, "https://bugs.launchpad.net/kabikaboo/+filebug", gtk.gdk.CURRENT_TIME))
        menu_item = self.builder.get_object("imagemenuitem_about")
        menu_item.connect("activate", self.about_callback)
        menu_item = self.builder.get_object("imagemenuitem_preferences")
        menu_item.connect("activate", self.settings_callback)
        menu_item = self.builder.get_object("menuitem_export_document")
        menu_item.connect("activate", self.export_document_callback)
        menu_item = self.builder.get_object("menuitem_stats")
        menu_item.connect("activate", self.statistics_callback)
        # close tab callback
        self.close_current_notebook_page_menu_item = self.builder.get_object("imagemenuitem_close_current_page")
        self.close_current_notebook_page_menu_item.connect("activate", self.close_current_notebook_page_callback)
        # export buttons
        self.export_node_menu_item = self.builder.get_object("menuitem_export_node")
        self.export_node_menu_item.connect("activate", self.export_node_callback)
        self.export_node_children_menu_item = self.builder.get_object("menuitem_export_node_children")
        self.export_node_children_menu_item.connect("activate", self.export_node_children_callback)
        self.import_text_menu_item = self.builder.get_object("menuitem_import_text")
        self.import_text_menu_item.connect("activate", self.import_text_callback)
        menu_item = self.builder.get_object("menuitem_export_html_document")
        menu_item.connect("activate", self.export_html_document_callback)
        self.export_html_node_menu_item = self.builder.get_object("menuitem_export_html_node")
        self.export_html_node_menu_item.connect("activate", self.export_html_node_callback)
        self.export_html_node_children_menu_item = self.builder.get_object("menuitem_export_html_node_children")
        self.export_html_node_children_menu_item.connect("activate", self.export_html_node_children_callback)
        self.autoopen_menu_item = self.builder.get_object("menuitem_autoopen")
        self.autoopen_menu_item.connect("toggled", self.autoopen_menu_item_toggle)
        self.save_on_exit_menu_item = self.builder.get_object("menuitem_saveonexit")
        self.save_on_exit_menu_item.connect("toggled", self.save_on_exit_menu_item_toggle)
        self.autosave_menu_item = self.builder.get_object("checkmenuitem_autosave")
        self.autosave_menu_item.connect("toggled", self.autosave_menu_item_toggle)
        self.spellcheck_menu_item = self.builder.get_object("checkmenuitem_spellcheck")
        self.spellcheck_menu_item.connect("toggled", self.spellcheck_menu_item_toggle)
        self.split_one_menu_item = self.builder.get_object("menuitem_split_one")
        self.split_one_menu_item.connect("activate", self.split_node_one_callback)
        self.split_two_menu_item = self.builder.get_object("menuitem_split_two")
        self.split_two_menu_item.connect("activate", self.split_node_two_callback)
        self.unify_with_menu_item = self.builder.get_object("menuitem_unify_with")
        self.unify_with_menu_item.connect("activate", self.unify_with_callback)
        self.unify_without_menu_item = self.builder.get_object("menuitem_unify_without")
        self.unify_without_menu_item.connect("activate", self.unify_without_callback)

    # attributes init
    def connect_attributes_panel(self):
        self.radiobutton_edit = self.builder.get_object("radiobutton_edit")
        self.radiobutton_view = self.builder.get_object("radiobutton_view")
        self.checkbutton_children = self.builder.get_object("checkbutton_children")
        self.radiobutton_bulleting_none = self.builder.get_object("radiobutton_bulleting_none")
        self.radiobutton_bulleting_number = self.builder.get_object("radiobutton_bulleting_number")
        self.radiobutton_bulleting_alpha_upper = self.builder.get_object("radiobutton_bulleting_alpha_upper")
        self.radiobutton_bulleting_alpha_lower = self.builder.get_object("radiobutton_bulleting_alpha_lower")
        self.radiobutton_bulleting_roman_upper = self.builder.get_object("radiobutton_bulleting_roman_upper")
        self.radiobutton_bulleting_roman_lower = self.builder.get_object("radiobutton_bulleting_roman_lower")
        self.vpaned_left.connect('size-allocate', self.on_vpaned_left_size_allocate)
        self.radiobutton_edit.connect("toggled", self.radiobutton_edit_callback, "radiobutton_view")
        self.radiobutton_view.connect("toggled", self.radiobutton_view_callback, "radiobutton_edit")
        self.checkbutton_children.connect("toggled", self.checkbutton_children_callback)
        self.radiobutton_bulleting_none.connect("toggled", self.radiobutton_bulleting_none_callback, "radiobutton_bulleting_none")
        self.radiobutton_bulleting_number.connect("toggled", self.radiobutton_bulleting_number_callback, "radiobutton_bulleting_number")
        self.radiobutton_bulleting_alpha_upper.connect("toggled", self.radiobutton_bulleting_alpha_upper_callback, "radiobutton_bulleting_alpha_upper")
        self.radiobutton_bulleting_alpha_lower.connect("toggled", self.radiobutton_bulleting_alpha_lower_callback, "radiobutton_bulleting_alpha_lower")
        self.radiobutton_bulleting_roman_upper.connect("toggled", self.radiobutton_bulleting_roman_upper_callback, "radiobutton_bulleting_roman_upper")
        self.radiobutton_bulleting_roman_lower.connect("toggled", self.radiobutton_bulleting_roman_lower_callback, "radiobutton_bulleting_roman_lower")

    # callback for undo, redo, cut, copy and paste
    def cut_callback(self, data=None):
        self.current_buffer.cut_clipboard(gtk.Clipboard(), True)
    def copy_callback(self, data=None):
        self.current_buffer.copy_clipboard(gtk.Clipboard())
    def paste_callback(self, data=None):
        self.current_buffer.paste_clipboard(gtk.Clipboard(), None, True)
    def undo_callback(self, menuitem, data=None):
        if self.current_buffer.can_undo():
            self.current_buffer.undo()
    def redo_callback(self, menuitem, data=None):
        if self.current_buffer.can_redo():
            self.current_buffer.redo()

    # callback for help
    # gnome-help will looks for help file in /usr/share/gnome/help/kabikaboo/
    # so the default English help will be /usr/share/gnome/help/kabikaboo/C/kabikaboo.xml
    def help_callback(self, data=None):
        if os.path.isdir('/usr/share/gnome/help/kabikaboo/'):
            props = { gnome.PARAM_APP_DATADIR : '/usr/share' }
            gnome.program_init('kabikaboo', '1.7', properties=props)
            gnome.help_display('kabikaboo')
        else:
            helpError='yelp requires help files to be stored in a very specific location.\n\
Try sudo cp -R help/ /usr/share/gnome/help/kabikaboo/ and restart Kabikaboo.'
            print helpError
            helpDialog = gtk.MessageDialog(parent=None, flags=0, type=gtk.MESSAGE_INFO,
             buttons=gtk.BUTTONS_CLOSE, message_format=helpError)
            response = helpDialog.run()
            if response == gtk.RESPONSE_CLOSE:
                helpDialog.destroy()

    # callback for new child node
    def new_child_node_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            new = self.document.add_node(self.editor_node, 'new', '')
            new_iter = self.add_document_node_to_tree(new, self.editor_iter)
            if not self.row_expanded(self.editor_iter):
                self.expand_row(self.editor_iter)
            self.bump()
            self.update_tool_buttons()
            self.update_textview_safe()
            self.update_attributes()
            self.update_tree_node_titles(self.editor_node)
            if self.file.move_on_new:
                self.editor_node = new
                self.editor_iter = new_iter
                path = self.treeview.get_model().get_path(new_iter)
                self.treeview.expand_to_path(path)
                self.treeview.scroll_to_cell(path)
                self.treeview.set_cursor(path)
                self.treeview.grab_focus()
                self.node_visit(new)

    # callback for move node
    def move_node_up_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            if self.document.can_move_up(self.editor_node):
                move_node = self.document.get_move_up_node(self.editor_node)
                self.find_iter_by_id(move_node.id)
                if self.found:
                    self.treestore.swap(self.editor_iter, self.found)
                    self.document.move_node_up(self.editor_node)
                    self.bump()
            self.update_tool_buttons()
            self.update_textview_safe()
            self.update_notebook_iters()
            self.update_node_path()
            self.update_tree_node_titles(self.editor_node)
            self.update_bookmarks()
            self.update_notebook()

    # callback for move node
    def move_node_down_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            if self.document.can_move_down(self.editor_node):
                move_node = self.document.get_move_down_node(self.editor_node)
                self.find_iter_by_id(move_node.id)
                if self.found:
                    self.treestore.swap(self.editor_iter, self.found)
                    self.document.move_node_down(self.editor_node)
                    self.bump()
            self.update_tool_buttons()
            self.update_textview_safe()
            self.update_notebook_iters()
            self.update_node_path()
            self.update_tree_node_titles(self.editor_node)
            self.update_bookmarks()
            self.update_notebook()

    # callback for move node
    def move_node_left_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            if self.document.can_move_left(self.editor_node):
                self.find_parent_iter_of(self.editor_node)
                sibling_iter = self.found
                self.find_parent_iter_of(self.editor_node.parent)
                parent_iter = self.found
                new_iter = self.insert_after_node_in_tree(self.editor_node, parent_iter, sibling_iter)
                old_iter = self.editor_iter
                self.document.move_node_left(self.editor_node)
                self.editor_iter = new_iter
                path = self.treestore.get_path(self.editor_iter)
                self.treeview.set_cursor(path)
                self.treestore.remove(old_iter)
                self.bump()
            self.update_tool_buttons()
            self.update_textview_safe()
            self.update_notebook_iters()
            self.update_node_path()
            self.update_tree_node_titles(self.editor_node)
            self.update_bookmarks()
            self.update_notebook()

    # callback for move node
    def move_node_right_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            if self.document.can_move_right(self.editor_node):
                new_parent_node = self.document.get_node_before(self.editor_node)
                self.find_iter_by_id(new_parent_node.id)
                new_parent_iter = self.found
                old_node = self.editor_node
                new_iter = self.add_document_node_to_tree(old_node, new_parent_iter)
                old_iter = self.editor_iter
                self.document.move_node_right(self.editor_node)
                self.editor_iter = new_iter
                path = self.treestore.get_path(self.editor_iter)
                if not self.row_expanded(new_parent_iter):
                    self.expand_row(new_parent_iter)
                self.treeview.set_cursor(path)
                self.treestore.remove(old_iter)
                self.bump()
            self.update_tool_buttons()
            self.update_textview_safe()
            self.update_notebook_iters()
            self.update_node_path()
            self.update_tree_node_titles(self.editor_node)
            self.update_bookmarks()
            self.update_notebook()

    # callback for new
    def new_document_callback(self, data=None):
        allow_new = True
        if self.file.different:
            allow_new = False
            dialog = gtk.MessageDialog(self.window, 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_INFO, 
                gtk.BUTTONS_YES_NO, 
                'You have not saved your current document.\nContinue?')
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                allow_new = True
        if allow_new:
            self.book_node_ids = []
            # note book tabs list of iter pointers
            self.book_iters = []
            # note book tab textviews (one on each page)
            self.book_textviews = []
            self.book_page = -1
            # pointers
            self.current_page = None
            self.last_page = None
            self.current_textview = None
            self.editor_node = None
            self.editor_iter = None
            self.file.new(self.document)
            self.populate_interface()
            self.default_view()
            self.document.post_load()
            self.unbump()
            self.start_time = time.time()
            if self.file.calculate_statistics:
                self.start_word_count = self.document.word_count()
            if self.statistics:
                self.statistics.new_data(self.document)

    # callback for open
    def open_document_callback(self, data=None):
        chooser = gtk.FileChooserDialog(title="Open Kabikaboo Document", parent=None, 
        action=gtk.FILE_CHOOSER_ACTION_OPEN,
        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("Kaboo documents")
        # might be useful to add in the future
        # filter.add_mime_type("text/kaboo")
        filter.add_pattern("*.kaboo")
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if self.file.working_file != '':
            chooser.set_current_folder(self.file.last_directory)
        elif self.file.last_directory != '':
            chooser.set_current_folder(self.file.last_directory)
        else:
            home = os.path.expanduser('~')
            chooser.set_folder_name(os.path.join(home, 'Documents'))
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.open_file(chooser.get_filename(), chooser)
            chooser.destroy()
        elif response == gtk.RESPONSE_CANCEL:
            chooser.destroy()

    # file handler
    def open_file(self, filename, dialog=None):
        result, new_document = self.file.load_from_file(filename)
        # open succeeded
        if result:
            self.document = new_document
            # update gui
            self.populate_interface()
            self.open_first_notebook_tab()
            self.update_history()
            # upgrade?
            if not self.file.upgraded:
                self.unbump()
            if dialog:
                dialog.destroy()
            if self.file.upgraded:
                dialog2 = gtk.MessageDialog(self.window, 
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                    gtk.MESSAGE_INFO, 
                    gtk.BUTTONS_OK, 
                    self.file.load_file_message)
                response = dialog2.run()
                dialog2.destroy()
            # run some post loading logic
            self.document.post_load()
            # mark the current time
            self.start_time = time.time()
            # calculate statistics on startup (if enabled)
            if self.file.calculate_statistics:
                self.start_word_count = self.document.word_count()
            if self.statistics:
                self.statistics.new_data(self.document)
        # open failed
        else:
            dialog2 = gtk.MessageDialog(self.window, 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_INFO, 
                gtk.BUTTONS_OK, 
                'Error opening file.')
            response = dialog2.run()
            dialog2.destroy()
        return result

    # opens the last file, maybe
    def open_file_on_startup(self):
        # file open flag
        file_opened = False
        # check for passed argument (filename)
        if len(sys.argv) >=2:
            file_opened, opened_document = self.file.load_from_file(sys.argv[1])
            if file_opened:
                self.document = opened_document
                # after we load do this
                self.document.post_load()
            else:
                print 'Failed to open file from command line: %s' % sys.argv[1]
        # try to open file from settings file
        else:
            allow_open_last_file = True
            # detect program crash
            if not self.file.proper_shutdown:
                if self.file.opened_attempts >= self.file.max_open_attempts:
                    allow_open_last_file = False
                    print 'Not opening last file (%d failed attempts)...' % self.file.opened_attempts
                '''message = "Program crash detected on last run.\nNot loading last opened document."
                dialog = gtk.MessageDialog(self.window, 
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                    gtk.MESSAGE_INFO, 
                    gtk.BUTTONS_OK, 
                    "Kabikaboo Crash Alert\n\n" + message)
                response = dialog.run()
                dialog.destroy()'''
            # open the file if no previous crash
            if allow_open_last_file:
                # open last file
                file_opened, opened_document = self.file.open(self.document)
                self.file.opened_attempts += 1
                self.file.save_recovery(False)
                if file_opened:
                    self.document = opened_document
                    # do post loading logic
                    self.document.post_load()
            # warn about upgrades
            if self.file.upgraded:
                dialog = gtk.MessageDialog(self.window, 
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                    gtk.MESSAGE_INFO, 
                    gtk.BUTTONS_OK, 
                    self.file.load_file_message)
                response = dialog.run()
                dialog.destroy()
        # if no file, use default data
        if not file_opened:
            if self.file.sample_data:
                self.document.generate_test_data()
            else:
                self.file.new(self.document)
            self.document.post_load()
            self.file.working_file = ''

    # callback for save
    def save_document_callback(self, data=None):
        if self.file.working_file != '':
            result = self.file.save(self.document)
        else:
            self.save_as_document_callback(data)
        self.unbump()
        self.update_history()
        self.update_status_bar()

    # callback for save version
    def save_version_callback(self, data=None):
        self.save_version()

    # save a new version
    def save_version(self):
        result, version = self.file.save_version(self.document)
        self.unbump()
        self.update_history()
        self.update_status_bar('Version %d saved.' % version)

    # callback for save as
    def save_as_document_callback(self, data=None):
        chooser = gtk.FileChooserDialog(title="Save Kabikaboo Document - " + self.document.title,
        parent=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("Kaboo documents")
        filter.add_pattern("*.kaboo")
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if self.file.working_file != '':
            chooser.set_current_folder(self.file.last_directory)
            chooser.set_current_name(self.file.working_file)
        elif self.file.last_directory != '':
            chooser.set_current_folder(self.file.last_directory)
            chooser.set_current_name(self.document.title + '.kaboo')
        else:
            home = os.path.expanduser('~')
            chooser.set_current_folder(os.path.join(home, 'Documents'))
            chooser.set_current_name(self.document.title + '.kaboo')
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.file.save_to_file(chooser.get_filename(), self.document)
            self.unbump()
            self.update_status_bar()
            self.update_history()
            self.open_file(chooser.get_filename(), chooser)
            chooser.destroy()
        elif response == gtk.RESPONSE_CANCEL:
            chooser.destroy()

    # callback for save copy
    def save_copy_callback(self, data=None):
        chooser = gtk.FileChooserDialog(title="Save Copy of Kabikaboo Document - " + self.document.title,
        parent=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
        buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name("Kaboo documents")
        filter.add_pattern("*.kaboo")
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if self.file.working_file != '':
            chooser.set_current_folder(self.file.last_directory)
            chooser.set_current_name(self.file.working_file)
        elif self.file.last_directory != '':
            chooser.set_current_folder(self.file.last_directory)
            chooser.set_current_name(self.document.title + '.kaboo')
        else:
            home = os.path.expanduser('~')
            chooser.set_current_folder(os.path.join(home, 'Documents'))
            chooser.set_current_name(self.document.title + '.kaboo')    
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.file.save_to_file(chooser.get_filename(), self.document)
            self.unbump()
            self.update_status_bar()
            self.update_history()
            self.open_file(chooser.get_filename(), chooser)
            chooser.destroy()
        elif response == gtk.RESPONSE_CANCEL:
            chooser.destroy()

    # callback for new node before
    def new_node_before_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            parent = self.find_parent_iter_of(self.editor_node)
            new = self.document.add_node_before(self.editor_node, 'new', '')
            if new:
                new_iter = self.insert_before_node_in_tree(new, parent, self.editor_iter)
                self.bump()
                self.update_tool_buttons()
                self.update_textview_safe()
                self.update_tree_node_titles(self.editor_node)
                if self.file.move_on_new:
                    self.editor_node = new
                    self.editor_iter = new_iter
                    path = self.treeview.get_model().get_path(new_iter)
                    self.treeview.expand_to_path(path)
                    self.treeview.scroll_to_cell(path)
                    self.treeview.set_cursor(path)
                    self.treeview.grab_focus()
                    self.node_visit(new)

    # callback for new node after
    def new_node_after_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            parent = self.find_parent_iter_of(self.editor_node)
            new = self.document.add_node_after(self.editor_node, 'new', '')
            if new:
                new_iter = self.insert_after_node_in_tree(new, parent, self.editor_iter)
                self.bump()
                self.update_tool_buttons()
                self.update_textview_safe()
                self.update_tree_node_titles(self.editor_node)
                if self.file.move_on_new:
                    self.editor_node = new
                    self.editor_iter = new_iter
                    path = self.treeview.get_model().get_path(new_iter)
                    self.treeview.expand_to_path(path)
                    self.treeview.scroll_to_cell(path)
                    self.treeview.set_cursor(path)
                    self.treeview.grab_focus()
                    self.node_visit(new)

    # callback for remove node
    def remove_node_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            message = "Remove '"+self.editor_node.title+"'"
            if self.editor_node.has_children():
                message += "\nand all of its children?"
            else:
                message += "?"
            dialog = gtk.MessageDialog(self.window, 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_INFO, 
                gtk.BUTTONS_YES_NO, 
                message)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                # try and delete the node
                if self.document.remove_node(self.editor_node):
                    parent = self.editor_node.parent
                    self.prune_dead_nodes()
                    self.editor_node = None
                    self.editor_iter = None
                    self.treeview.get_selection().unselect_all()
                    self.bump()
                    self.update_tool_buttons()
                    self.update_attributes()
                    self.update_notebook()
                    self.update_bookmarks()
                    self.update_node_path()
                    self.update_tree_node_titles(parent)
                    self.update_textview_safe()

    # callback for remove children of a node, but not the node
    def remove_children_callback(self, data=None):
        if self.editor_node and self.editor_iter:
            message = "Remove children of\n'"+self.editor_node.title+"'?"
            dialog = gtk.MessageDialog(self.window, 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_INFO, 
                gtk.BUTTONS_YES_NO, 
                message)
            response = dialog.run()
            dialog.destroy()
            if response == gtk.RESPONSE_YES:
                # try and delete the node
                self.remove_children()

    # remove children of a node, but not the node
    def remove_children(self, data=None):
        if self.editor_node and self.editor_iter:
            # try and delete the node
            if self.document.remove_children(self.editor_node):
                self.prune_dead_nodes()
                self.bump()
                self.update_tool_buttons()
                self.update_textview_safe()
                self.update_notebook()
                self.update_bookmarks()
                self.update_attributes()

    # callback for remove node
    def expand_all_nodes_callback(self, data=None):
        self.expand_all_nodes()
        self.update_tool_buttons()

    # expand all children of a node
    def expand_all_children_callback(self, data=None):
        if self.editor_iter:
            self.expand_all_children(self.editor_iter)
        self.update_tool_buttons()

    # collapse row
    def expand_row_callback(self, data=None):
        if self.editor_iter:
            self.expand_row(self.editor_iter)
        self.update_tool_buttons()

    # collapse row
    def collapse_row_callback(self, data=None):
        if self.editor_iter:
            self.collapse_row(self.editor_iter)
        self.update_tool_buttons()

    # callback refreshing the tree
    def refresh_tree_callback(self, data=None):
        self.refresh_tree()

    # callback for showing the default document view
    def default_view_callback(self, data=None):
        self.default_view()

    # recursively add document nodes to treeview
    def add_document_node_to_tree(self, node, top):
        iter = self.treestore.append(top, [node.get_title(), node.id])
        for child in node.children.list:
            self.add_document_node_to_tree(child, iter)
        return iter

    # recursively add document nodes to treeview
    def insert_before_node_in_tree(self, node, parent, sibling):
        iter = self.treestore.insert_before(parent, sibling, [node.get_title(), node.id])
        for child in node.children.list:
            self.add_document_node_to_tree(child, iter)
        return iter

    # recursively add document nodes to treeview
    def insert_after_node_in_tree(self, node, parent, sibling):
        iter = self.treestore.insert_after(parent, sibling, [node.get_title(), node.id])
        for child in node.children.list:
            self.add_document_node_to_tree(child, iter)
        return iter

    # add the first node form the document to the tree, then recurse
    def match_tree_to_document(self):
        self.add_document_node_to_tree(self.document, None)
        self.expand_document_node()

    # refresh the tree
    def refresh_tree(self):
        self.treestore.clear()
        self.add_document_node_to_tree(self.document, None)
        self.expand_document_node()
        self.editor_node = None
        self.editor_iter = None
        self.treeview.get_selection().unselect_all()
        self.update_textview()
        self.update_tool_buttons()
        self.update_attributes()
        self.update_node_path()
        self.update_tree_node_titles(self.document)

    # expand the first node
    def default_view(self):
        iter = self.treestore.get_iter_first()
        path = self.treestore.get_path(iter)
        self.treeview.collapse_row(path)
        self.treeview.expand_row(path, False)
        self.editor_node = self.document
        self.editor_iter = iter
        selection = self.treeview.get_selection()
        selection.select_iter(iter)
        self.add_to_notebook(self.editor_node, self.editor_iter)
        self.open_first_notebook_tab()
        self.update_tool_buttons()
        self.update_attributes()
        self.update_node_path()
        self.update_textview()
        self.node_visit(self.editor_node)

    # expand the first node
    def expand_document_node(self):
        iter = self.treestore.get_iter_first()
        path = self.treestore.get_path(iter)
        self.treeview.expand_row(path, False)

    # expand all nodes
    def expand_all_nodes(self):
        self.treeview.expand_all()

    # expand all nodes
    def expand_row(self, iter):
        path = self.treestore.get_path(iter)
        self.treeview.collapse_row(path)
        self.treeview.expand_row(path, False)

    # expand all nodes
    def expand_all_children(self, iter):
        path = self.treestore.get_path(iter)
        self.treeview.expand_row(path, True)

    # is this row expanded?
    def row_expanded(self, iter):
        path = self.treestore.get_path(iter)
        return self.treeview.row_expanded(path)

    # collapse a row
    def collapse_row(self, iter):
        path = self.treestore.get_path(iter)
        self.treeview.collapse_row(path)

    # collapse all nodes
    def collapse_all_nodes(self):
        self.treeview.collapse_all()
        expand_document_node()

    # find parent iter
    def find_parent_iter_of(self, node):
        iter = None
        if node.parent:
            self.find_iter_by_id(node.parent.id)
            iter = self.found
        return iter

    # find iter in tree, using id column
    def find_iter_by_id(self, id):
        found = None
        # callback on treestore.foreach
        def foreach_iter(model, path, iter, user_data):
            if iter:
                # find id
                this_id = model.get_value(iter, 1)
                # match parent id?
                if this_id == id:
                    found = iter
                    self.found = iter
                    return found
        # loop through entire tree, finding dead nodes
        self.treestore.foreach(foreach_iter, None)
        # success?
        return found

    # find and place a new node in the tree (we dont know where)
    def place_new_node_in_tree(self, node):
        # parent
        parent = None
        parent_iter = None
        if node.parent:
            # callback on treestore.foreach
            def foreach_iter(model, path, iter, user_data):
                if iter:
                    # find id
                    id = self.treestore.get_value(iter, 1)
                    # match parent id?
                    if id == node.parent.id:
                        parent_iter = iter
            # loop through entire tree, finding dead nodes
            self.treestore.foreach(foreach_iter, None)
            # success?
            self.add_document_node_to_tree(node, parent_iter)

    # check for deleted nodes
    def prune_dead_nodes(self):
        # make a list of dead nondes
        dead = []
        # callback on treestore.foreach
        def foreach_iter(model, path, iter, user_data):
            if iter:
                # find id
                id = self.treestore.get_value(iter, 1)
                # check id if it is in document
                if not self.document.valid_id(id):
                    # not valid id, add it to dead list
                    dead.append(iter)
        # loop through entire tree, finding dead nodes
        self.treestore.foreach(foreach_iter, None)
        # loop backwards thru dead list to remove nodes from treestore
        for node in reversed(dead):
            self.treestore.remove(node)

    # update the tree node titles, possibly just a subset
    def update_tree_node_titles(self, node):
        # parent
        if node:
            node_iter = self.find_iter_by_id(node.id)
            # callback on treestore.foreach
            def foreach_iter(model, path, iter, user_data):
                if iter:
                    # find id
                    this_id = model.get_value(iter, 1)
                    treenode = self.document.fetch_node_by_id(this_id)
                    # can maybe optimize this by only updating "node"'s children
                    if treenode:
                        self.treestore.set_value(iter, 0, treenode.get_title())
            # loop through entire tree, finding dead nodes
            self.treestore.foreach(foreach_iter, node)

    # bump the file to changed
    def bump(self):
        if self.file.working_file!='':
            self.file.different = True
            self.update_status_bar()
            self.set_window_title()

    # bump the file to unchanged
    def unbump(self):
        self.file.different = False
        self.update_status_bar()
        self.set_window_title()

    # maximize event
    def on_window_state_change(self, window, event):
        if event.new_window_state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
            self.file.window_maximized = True
        else:
            self.file.window_maximized = False

    # store the window size
    def on_window_size_allocate(self, window, requisition, userdate=None):
        self.file.window_width = requisition.width
        if not self.file.window_height == requisition.height:
            self.file.window_height = requisition.height
            self.vpaned_left.set_position(self.file.window_height - 180)

    # store the window position
    def on_window_move(self, window, properties, userdata=None):
        if not self.positioning:
            self.file.window_x = properties.x
            self.file.window_y = properties.y

    # callback for tree/text slider change
    def on_vpaned_left_size_allocate(self, widget, requisition, userdate=None):
        # resize node title label
        self.label_title.set_property("width-request", self.hpaned_main.get_position())

    def autoopen_menu_item_toggle(self, toggle, data=None):
        if not editor.building_gui:
            self.file.autoopen = self.autoopen_menu_item.get_active()
            self.file.save_settings_default()
            self.update_settings_window()

    def save_on_exit_menu_item_toggle(self, toggle, data=None):
        if not editor.building_gui:
            self.file.save_on_exit = self.save_on_exit_menu_item.get_active()
            self.file.save_settings_default()
            self.update_settings_window()

    def autosave_menu_item_toggle(self, toggle, data=None):
        if not editor.building_gui:
            self.file.autosave = self.autosave_menu_item.get_active()
            self.file.save_settings_default()
            self.update_settings_window()
            self.check_autosave()

    def export_document_callback(self, data=None):
        self.export_to_text(self.document, True)

    def export_node_callback(self, data=None):
        if self.editor_node:
            self.export_to_text(self.editor_node, False)

    def export_node_children_callback(self, data=None):
        if self.editor_node:
            self.export_to_text(self.editor_node, True)

    def export_to_text(self, node, recurse=True):
        chooser = gtk.FileChooserDialog(title='Export Kabikaboo Text Document - ' + self.document.title,
            parent=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name('.txt documents')
        filter.add_pattern('*.txt')
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name('Kaboo documents')
        filter.add_pattern('*.kaboo')
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name('All files')
        filter.add_pattern('*')
        chooser.add_filter(filter)
        if self.file.last_export_directory != '':
            chooser.set_current_folder(self.file.last_export_directory)
        else:
            home = os.path.expanduser('~')
            chooser.set_current_folder(os.path.join(home, 'Documents'))
        chooser.set_current_name(self.document.title + '.txt')
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.file.export_to_text_file(self.document, node, chooser.get_filename(), recurse, self.document.show_titles_in_export)
            chooser.destroy()
        elif response == gtk.RESPONSE_CANCEL:
            chooser.destroy()

    def export_html_document_callback(self, data=None):
        self.export_to_html(self.document, True)

    def export_html_node_callback(self, data=None):
        if self.editor_node:
            self.export_to_html(self.editor_node, False)

    def export_html_node_children_callback(self, data=None):
        if self.editor_node:
            self.export_to_html(self.editor_node, True)

    def export_to_html(self, node, recurse=True):
        chooser = gtk.FileChooserDialog(title='Export Kabikaboo HTML Document - ' + self.document.title,
            parent=None, action=gtk.FILE_CHOOSER_ACTION_SAVE,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_SAVE,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name('HTML documents')
        filter.add_pattern('*.html')
        filter.add_pattern('*.htm')
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name('Kaboo documents')
        filter.add_pattern('*.kaboo')
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name('All files')
        filter.add_pattern('*')
        chooser.add_filter(filter)
        if self.file.last_export_directory != '':
            chooser.set_current_folder(self.file.last_export_directory)
        else:
            home = os.path.expanduser('~')
            chooser.set_current_folder(os.path.join(home, 'Documents'))
        chooser.set_current_name(self.document.title + '.html')
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            self.file.export_to_html_file(self.document, node, chooser.get_filename(), recurse, self.document.show_titles_in_export)
            chooser.destroy()
        elif response == gtk.RESPONSE_CANCEL:
            chooser.destroy()

    def radiobutton_edit_callback(self, button, data=None):
        self.set_node_edit()
        self.update_tool_buttons()

    def radiobutton_view_callback(self, button, data=None):
        self.set_node_view()
        self.update_tool_buttons()

    def set_node_edit(self):
        if self.editor_node and not self.updating_attributes:
            if self.editor_node.view != False:
                self.editor_node.view = False
                self.bump()
                self.update_attributes()
                self.current_buffer.begin_not_undoable_action()
                self.update_textview()
                self.current_buffer.end_not_undoable_action()

    def set_node_view(self):
        if self.editor_node and not self.updating_attributes:
            if self.editor_node.view != True:
                self.editor_node.view = True
                self.bump()
                self.update_attributes()
                self.current_buffer.begin_not_undoable_action()
                self.update_textview()
                self.current_buffer.end_not_undoable_action()

    def flip_node_grandchildren(self):
        if self.editor_node and self.editor_node.view and not self.updating_attributes:
            self.editor_node.all = not self.editor_node.all
            self.bump()
            self.update_attributes()
            self.update_textview()

    def checkbutton_children_callback(self, toggle, data=None):
        if self.editor_node and not self.updating_attributes:
            if self.editor_node.all != self.checkbutton_children.get_active():
                self.editor_node.all = self.checkbutton_children.get_active()
                self.bump()
                self.update_attributes()
                self.update_textview()

    def radiobutton_bulleting_none_callback(self, button, data=None):
        if self.editor_node and not self.updating_attributes:
            self.editor_node.bulleting = self.editor_node.BULLETING_NONE
            self.bump()
            self.update_attributes()
            if self.editor_node.view:
                self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_notebook()

    def radiobutton_bulleting_number_callback(self, button, data=None):
        if self.editor_node and not self.updating_attributes:
            self.editor_node.bulleting = self.editor_node.BULLETING_NUMBER
            self.bump()
            self.update_attributes()
            if self.editor_node.view:
                self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_notebook()

    def radiobutton_bulleting_alpha_upper_callback(self, button, data=None):
        if self.editor_node and not self.updating_attributes:
            self.editor_node.bulleting = self.editor_node.BULLETING_ALPHA_UPPER
            self.bump()
            self.update_attributes()
            if self.editor_node.view:
                self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_notebook()

    def radiobutton_bulleting_alpha_lower_callback(self, button, data=None):
        if self.editor_node and not self.updating_attributes:
            self.editor_node.bulleting = self.editor_node.BULLETING_ALPHA_LOWER
            self.bump()
            self.update_attributes()
            if self.editor_node.view:
                self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_notebook()

    def radiobutton_bulleting_roman_upper_callback(self, button, data=None):
        if self.editor_node and not self.updating_attributes:
            self.editor_node.bulleting = self.editor_node.BULLETING_ROMAN_UPPER
            self.bump()
            self.update_attributes()
            if self.editor_node.view:
                self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_notebook()

    def radiobutton_bulleting_roman_lower_callback(self, button, data=None):
        if self.editor_node and not self.updating_attributes:
            self.editor_node.bulleting = self.editor_node.BULLETING_ROMAN_LOWER
            self.bump()
            self.update_attributes()
            if self.editor_node.view:
                self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_notebook()

    # update the attributes pane
    def update_attributes(self):
        if self.file.show_attributes:
            if self.editor_node and self.editor_iter and not self.updating_attributes:
                self.updating_attributes = True
                self.label_title.set_label('<b>'+self.editor_node.title+'</b>')
                self.label_title.set_tooltip_text(self.editor_node.get_recursive_title())
                if not self.editor_node.view:
                    self.radiobutton_edit.set_active(True)
                    self.checkbutton_children.set_property("visible", False)
                else:
                    if self.editor_node.all:
                        self.checkbutton_children.set_active(True)
                    else:
                        self.checkbutton_children.set_active(False)
                    self.radiobutton_view.set_active(True)
                    self.checkbutton_children.set_property("visible", True)
                if self.editor_node.bulleting == self.editor_node.BULLETING_NONE:
                    self.radiobutton_bulleting_none.set_active(True)
                if self.editor_node.bulleting == self.editor_node.BULLETING_NUMBER:
                    self.radiobutton_bulleting_number.set_active(True)
                if self.editor_node.bulleting == self.editor_node.BULLETING_ALPHA_UPPER:
                    self.radiobutton_bulleting_alpha_upper.set_active(True)
                if self.editor_node.bulleting == self.editor_node.BULLETING_ALPHA_LOWER:
                    self.radiobutton_bulleting_alpha_lower.set_active(True)
                if self.editor_node.bulleting == self.editor_node.BULLETING_ROMAN_UPPER:
                    self.radiobutton_bulleting_roman_upper.set_active(True)
                if self.editor_node.bulleting == self.editor_node.BULLETING_ROMAN_LOWER:
                    self.radiobutton_bulleting_roman_lower.set_active(True)
                if self.editor_node.has_children() and self.file.show_bullets:
                    self.fixed_node_bullet.set_property("visible", True)
                else:
                    self.fixed_node_bullet.set_property("visible", False)
                self.attributes_area.set_property("visible", True)
                self.updating_attributes = False
            else:
                self.attributes_area.set_property("visible", False)
        else:
            self.attributes_area.set_property("visible", False)

    def scroll_textview_callback(self, scrolled_window, scrollType, horizontal, data=None):
        if self.current_textview:
            self.current_textview.grab_focus()

    # add node to notebook at beginning of it (dont call this directly, use add_to_notebook instead)
    def prepend_to_notebook(self, node, iter):
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        scrolled_window.set_border_width(10)
        textbuffer = gtksourceview2.Buffer()
        textview = gtksourceview2.View(textbuffer)
        scrolled_window.add(textview)
        if self.file.tab_bullets:
            tab_title = node.get_spaced_bullet_title(14)
        else:
            tab_title = node.get_spaced_title(14)
        label = gtk.Label(tab_title)
        label.set_tooltip_text(node.get_recursive_title())
        scrolled_window.show()
        scrolled_window.connect("scroll-child", self.scroll_textview_callback)
        textview.show()
        # word wrap
        textview.set_wrap_mode(gtk.WRAP_WORD)
        # text view margins
        textview.set_right_margin(8)
        textview.set_left_margin(8)
        textview.set_pixels_above_lines(self.file.spaces_above)
        textview.set_pixels_below_lines(self.file.spaces_below)
        textview.set_pixels_inside_wrap(0)
        # text buffer tags
        textbuffer.create_tag("normal", weight=pango.WEIGHT_NORMAL, family="verdana")
        textbuffer.create_tag("bold", weight=pango.WEIGHT_BOLD)
        textbuffer.create_tag("italic", style=pango.STYLE_ITALIC)
        textbuffer.create_tag("underline", underline=pango.UNDERLINE_SINGLE)
        textbuffer.create_tag("small", scale=pango.SCALE_SMALL, weight=pango.SCALE_SMALL, family="verdana")
        label.show()
        self.notebook.prepend_page(scrolled_window, label)
        self.book_node_ids.insert(0, node.id)
        self.book_iters.insert(0, iter)
        self.book_textviews.insert(0, textview)
        #update the text
        self.current_textview = textview
        self.current_buffer = textbuffer
        self.editor_iter = iter
        self.editor_node = node
        #gtkspell
        if(self.file.spellcheck):
            gtkspell.Spell(textview, lang=None)
        self.update_textview()

    # add node to notebook
    def add_to_notebook(self, node, iter):
        if self.document.tab_max < 1:
            return
        (added, moved, changed, duplicate, overflow, previousIndex, newIndex) = self.document.add_tab(node)
        if changed:
            if added:
                self.changing_cursor = True
                self.prepend_to_notebook(node, iter)
                self.notebook_switch_node(node)
                self.changing_cursor = False
            if moved:
                self.changing_cursor = True
                if previousIndex >= 0:
                    book_textview = self.book_textviews[previousIndex]
                    book_iter = self.book_iters[previousIndex]
                    book_node_id = self.book_node_ids[previousIndex]
                    del self.book_textviews[previousIndex]
                    del self.book_iters[previousIndex]
                    del self.book_node_ids[previousIndex]
                self.book_textviews.insert(0, book_textview)
                self.book_iters.insert(0, book_iter)
                self.book_node_ids.insert(0, book_node_id)
                self.book_page = 0
                # change the gui notebook
                if previousIndex >= 0:
                    page = self.notebook.get_nth_page(previousIndex)
                    if page>-1:
                        self.notebook.reorder_child(page, 0)
                self.notebook_switch_node(node)
                self.changing_cursor = False
            if overflow:
                self.check_notebook()
            #self.verify_notebook()

    def close_notebook_page(self, node):
        if node.id in self.book_node_ids:
            self.changing_cursor = True
            self.switching_page = True
            index = self.book_node_ids.index(node.id)
            if(len(self.book_node_ids) > 1):
                new_index = index + 1
                if(new_index >= len(self.book_node_ids)):
                    new_index = 0
                self.current_textview = self.book_textviews[new_index]
                self.current_buffer = self.current_textview.get_buffer()
                self.editor_iter = self.book_iters[new_index]
                self.editor_node = self.document.fetch_node_by_id(self.book_node_ids[new_index])
                path = self.treeview.get_model().get_path(self.editor_iter)
                self.treeview.expand_to_path(path)
                self.treeview.set_cursor(path)
                # when the user changes the text, call this
                self.current_buffer.connect("changed", self.text_changed_callback)
                self.current_textview.connect("populate-popup", self.textview_populate_popup_callback)
                self.current_textview.connect('key-press-event', self.textview_key_press_callback)
                # key press on textview
                self.update_attributes()
                self.update_tool_buttons()
                self.update_node_path()
                #self.update_textview()
                self.notebook.set_current_page(new_index)
                # visit this node
                self.node_visit(self.editor_node)
                #self.blank_hidden_tabs(self.editor_node)
                self.book_page = index
            # remove node from list
            self.document.remove_tab(node)
            self.book_textviews.remove(self.book_textviews[index])
            self.book_iters.remove(self.book_iters[index])
            self.book_node_ids.remove(self.book_node_ids[index])
            self.notebook.remove_page(index)
            self.changing_cursor = False
            self.switching_page = False
            # was that the last page?
            if len(self.book_node_ids) == 0:
                self.book_page = -1

    def close_current_notebook_page(self):
        if self.editor_node:
            self.close_notebook_page(self.editor_node)
        self.update_tool_buttons()
        self.update_node_path()

    def close_current_notebook_page_callback(self, data=None):
        self.close_current_notebook_page()

    def next_notebook_page(self):
        #self.verify_notebook()
        if not self.switching_page and len(self.document.tabs) > 0:
            page_num = self.book_page + 1
            if page_num >= len(self.document.tabs):
                page_num = 0
            node = self.document.fetch_node_by_id(self.book_node_ids[page_num])
            self.notebook_switch_node(node)
            self.node_visit(node)

    def previous_notebook_page(self):
        #self.verify_notebook()
        if not self.switching_page and len(self.document.tabs) > 0:
            page_num = self.book_page - 1
            if page_num < 0:
                page_num = len(self.document.tabs) - 1
            node = self.document.fetch_node_by_id(self.book_node_ids[page_num])
            self.notebook_switch_node(node)
            self.node_visit(node)

    # called when user selects a new tab
    def notebook_switch_page_callback(self, notebook, page, page_num):
        if not self.switching_page:
            if page_num >= 0 and self.book_page != page_num and page_num < len(self.book_textviews):
                self.changing_cursor = True
                self.current_textview = self.book_textviews[page_num]
                self.current_buffer = self.current_textview.get_buffer()
                self.editor_iter = self.book_iters[page_num]
                self.editor_node = self.document.fetch_node_by_id(self.book_node_ids[page_num])
                path = self.treeview.get_model().get_path(self.editor_iter)
                self.treeview.expand_to_path(path)
                self.treeview.set_cursor(path)
                # when the user changes the text, call this
                self.current_buffer.connect("changed", self.text_changed_callback)
                self.current_textview.connect("populate-popup", self.textview_populate_popup_callback)
                self.current_textview.connect('key-press-event', self.textview_key_press_callback)
                # todo: hook into context menu via "populate-popup" callback
                self.book_page = page_num
                #self.blank_hidden_tabs(self.editor_node)
                self.update_attributes()
                self.update_tool_buttons()
                self.update_node_path()
                #self.update_textview()
                self.node_visit(self.editor_node)
                self.changing_cursor = False

    # force the notebook to switch to a node (which must be already in the notebook)
    #  usually happens from ctrl+tab or treeview
    def notebook_switch_node(self, node):
        result = False
        if node.id in self.book_node_ids:
            self.changing_cursor = True
            self.switching_page = True
            index = self.book_node_ids.index(node.id)
            self.current_textview = self.book_textviews[index]
            self.current_buffer = self.current_textview.get_buffer()
            self.editor_iter = self.book_iters[index]
            self.editor_node = self.document.fetch_node_by_id(self.book_node_ids[index])
            path = self.treeview.get_model().get_path(self.editor_iter)
            self.treeview.expand_to_path(path)
            self.treeview.set_cursor(path)
            # when the user changes the text, call this
            self.current_buffer.connect("changed", self.text_changed_callback)
            self.current_textview.connect("populate-popup", self.textview_populate_popup_callback)
            self.current_textview.connect('key-press-event', self.textview_key_press_callback)
            self.book_page = index
            # key press on textview
            self.update_attributes()
            self.update_tool_buttons()
            self.update_node_path()
            #self.update_textview()
            self.notebook.set_current_page(index)
            #self.blank_hidden_tabs(self.editor_node)
            self.changing_cursor = False
            self.switching_page = False
            result = True
        return result

    # check the notebook for too many tabs
    def check_notebook(self):
        while(len(self.book_node_ids) > self.document.tab_max):
            self.book_textviews.remove(self.book_textviews[len(self.book_textviews)-1])
            self.book_iters.remove(self.book_iters[len(self.book_iters)-1])
            self.book_node_ids.remove(self.book_node_ids[len(self.book_node_ids)-1])
            self.notebook.remove_page(-1)

    # verify that the notebook is correct
    def verify_notebook(self):
        mismatch = False
        if len(self.document.tabs) != len(self.book_node_ids):
            print 'book_node_ids out of sync %d ' % len(self.document.tabs)
            print 'book_node_ids out of sync %d ' % len(self.book_node_ids)
            mismatch = True
        if len(self.document.tabs) != len(self.book_textviews):
            print 'book_textviews out of sync %d ' % len(self.document.tabs)
            print 'book_textviews out of sync %d ' % len(self.book_textviews)
            mismatch = True
        if len(self.document.tabs) != len(self.book_iters):
            print 'book_iters out of sync %d ' % len(self.document.tabs)
            print 'book_iters out of sync %d ' % len(self.book_iters)
            mismatch = True
        if not mismatch:
            for index, node_id in enumerate(self.document.tabs):
                if node_id != self.book_node_ids[index]:
                    print 'book mismatch at index %d' % index

    # remove any notebook pages, and rebuild all tabs
    def match_notebook_to_document(self):
        while self.notebook.get_n_pages() > 0:
            self.notebook.remove_page(0)
        if len(self.document.tabs)>0:
            self.document.tabs.reverse()
            node = None
            unfound = False
            missing = []
            for node_id in self.document.tabs:
                search = self.document.fetch_node_by_id(node_id)
                if search:
                    node = search
                    self.find_iter_by_id(node_id)
                    if self.found != None:
                        iter = self.found
                        self.changing_cursor = True
                        self.switching_page = True
                        self.prepend_to_notebook(node, iter)
                        self.changing_cursor = False
                        self.switching_page = False
                    else:
                        print 'Error: NoteBook Tab not found!'
                        print node_id
                else:
                    # user had less than tab_max tabs open
                    unfound = True
                    print 'Tab node unfound in document (id = %d)' % node_id
                    missing.append(node_id)
            self.document.tabs.reverse()
            # remove any unfound nodes (not ideal, but prevents corruption)
            if unfound:
                for node_id in missing:
                    self.document.tabs.remove(node_id)
        #self.verify_notebook()

    # opens the first tab
    def open_first_notebook_tab(self):
        self.document.tabs.reverse()
        node = None
        for node_id in self.document.tabs:
            search = self.document.fetch_node_by_id(node_id)
            if search:
                node = search
        self.document.tabs.reverse()
        # take the last node and "click it"
        if node:
            self.notebook_switch_node(node)

    # detect and update any changes in the notebook
    def update_notebook(self):
        # check for deleted nodes
        deleted_nodes = []
        for node_id in self.book_node_ids:
            if not self.document.fetch_node_by_id(node_id):
                deleted_nodes.append(node_id)
        # remove deleted nodes
        for node_id in deleted_nodes:
            index = self.book_node_ids.index(node_id)
            del self.book_node_ids[index]
            del self.book_iters[index]
            del self.book_textviews[index]
            self.notebook.remove_page(index)
            if len(self.book_node_ids) > 0:
                if self.book_page == index:
                    self.notebook_switch_node(self.document.fetch_node_by_id(self.book_node_ids[0]))
            else:
                self.editor_iter = None
                self.editor_node = None
                self.current_textview = None
                self.current_buffer = None
        # check for changed labels
        for index, node_id in enumerate(self.book_node_ids):
            node = self.document.fetch_node_by_id(node_id)
            page = self.notebook.get_nth_page(index)
            label = self.notebook.get_tab_label(page)
            if self.file.tab_bullets:
                tab_title = node.get_spaced_bullet_title(14)
            else:
                tab_title = node.get_spaced_title(14)
            if label.get_text() != tab_title:
                label.set_text(tab_title)
            tab_tip = node.get_recursive_title()
            if label.get_tooltip_text() != tab_tip:
                label.set_tooltip_text(tab_tip)

    # if the treeview changes, we should adjust the notebook iter pointers
    def update_notebook_iters(self):
        # check for moved iters
        for index, node_id in enumerate(self.book_node_ids):
            self.find_iter_by_id(node_id)
            if self.found != None:
                self.book_iters[index] = self.found

    # this could be used to optimize the notebook (not used currently)
    # in the future, this should be optional
    def blank_hidden_tabs(self, shown_node):
        # blank view tabs (for speed)
        for index, node_id in enumerate(self.book_node_ids):
            if node_id != shown_node.id:
                node = self.document.fetch_node_by_id(node_id)
                # dont blank edit pages, because of undo/redo
                if node.view:
                    textview = self.book_textviews[index]
                    buffer = textview.get_buffer()
                    self.copying_buffer = True
                    buffer.set_text('')
                    self.copying_buffer = False

    # copy text into the textview's buffer
    # needs wrapper due to callbacks being sprung during set_text
    def set_textbuffer(self, text):
        if self.current_textview:
            self.copying_buffer = True
            self.current_buffer.set_text(text)
            self.copying_buffer = False

    # add highlighting etc
    def fancy_text(self, node):
        self.set_textbuffer('')
        iter = self.current_buffer.get_start_iter()
        self.current_buffer.insert_with_tags_by_name(iter, '\n', "normal")
        self.fancy_text_node(iter, node, '', node.all, True)

    # fancy text
    def fancy_text_node(self, iter, node, title, recurse, first):
        text = ''
        if self.document.show_titles_in_view:
            self.current_buffer.insert_with_tags_by_name(iter, node.get_title(), "bold")
            if title:
                title = title + ' -> ' + node.get_title()
                self.current_buffer.insert_with_tags_by_name(iter, '\n', "normal")
                self.current_buffer.insert_with_tags_by_name(iter, title, "small")
            else:
                title = node.get_title()
            text = '\n'
            text +=  '-' * 2 * len(title)
            text +=  '\n'
        if(node.text):
            text +=  node.text
            text +=  '\n\n'
        self.current_buffer.insert_with_tags_by_name(iter, text, "normal")
        if recurse or first:
            for child in node.children.list:
                self.fancy_text_node(iter, child, title, recurse, False)

    # callback for about
    def about_callback(self, data=None):
        authors = [
            "David Glen Kerr",
            "Jeremy Bicha",
        ]
        about = gobject.new(
            gtk.AboutDialog, name='Kabikaboo',
            version=current_version(), copyright='© 2008-2009 David Kerr and Jeremy Bicha\n'
            + 'Open source; free for all to use and modify.',
            comments="Recursive Writing Assistance Software")
        about.set_program_name('Kabikaboo')
        about.set_transient_for(self.window)
        about.set_website('https://launchpad.net/kabikaboo')
        about.set_logo(None)
        about.set_wrap_license(True)
        license='''Kabikaboo is free software: you can redistribute it and/or  \
modify it under the terms of the GNU General Public License as published by the \
Free Software Foundation, either version 2 of the License, or (at your option) \
any later version.\n
Kabikaboo is distributed in the hope that it will be useful, but WITHOUT ANY \
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR \
A PARTICULAR PURPOSE. See the GNU General Public License for more details.\n
You should have received a copy of the GNU General Public License along with  \
Kabikaboo. If not, see http://www.gnu.org/licenses/.'''
        about.set_license(license)
        response = about.run()
        about.hide()

    # callback for settings window
    def settings_callback(self, data=None):
        new_settings = True
        if self.settings:
            if self.settings.window and self.settings.window.get_property('visible'):
                self.settings.window.deiconify()
                self.settings.window.show()
                self.settings.window.set_keep_above(False)
                new_settings = False
        if new_settings:
            self.settings = KabikabooSettingsWindow()
            self.settings.set_data(self, self.file, self.document)
            self.settings.populate_settings()
            self.settings.window.show()

    # callback from settings menu
    def update_settings(self):
        self.apply_settings()

    # apply most settings to kabikaboo's main window
    def apply_settings(self):
        # tool bar - text on buttons
        if self.file.tool_text:
            self.toolbar_tree.set_style(gtk.TOOLBAR_BOTH)
        else:
            self.toolbar_tree.set_style(gtk.TOOLBAR_ICONS)
        if self.file.show_toolbar_tree:
            self.toolbar_tree.show()
        else:
            self.toolbar_tree.hide()
        # text tool bar
        if self.file.show_toolbar_text:
            self.toolbar_text.show()
        else:
            self.toolbar_text.hide()
        # status bar
        if self.file.show_statusbar:
            self.statusbar.show()
        else:
            self.statusbar.hide()
        # attributes
        if self.file.show_attributes:
            self.attributes_area.show()
            self.update_attributes()
        else:
            self.attributes_area.hide()
        # status
        self.update_status_bar()
        # tab arrows
        self.notebook.set_scrollable(self.file.show_tab_arrows)
        # homog tabs
        self.notebook.set_property('homogeneous', self.file.homog_tabs)
        # show tabs
        self.notebook.set_show_tabs(self.file.show_tabs)
        # autosave / autoopen
        self.autoopen_menu_item.set_active(self.file.autoopen)        
        self.save_on_exit_menu_item.set_active(self.file.save_on_exit)
        self.autosave_menu_item.set_active(self.file.autosave)
        # spellcheck
        self.spellcheck_menu_item.set_active(self.file.spellcheck)
        # view
        self.show_attributes_menu_item.set_active(self.file.show_attributes)
        self.show_statusbar_menu_item.set_active(self.file.show_statusbar)
        self.show_toolbar_tree_menu_item.set_active(self.file.show_toolbar_tree)

    # update the settings window, if open
    def update_settings_window(self):
        if self.settings:
            self.settings.populate_settings()

    ''' HISTORY '''
    # history init
    def create_history_gui(self):
        self.history_action = gtk.Action('recentmenu', 'Open _Recent', None, None)
        self.history_menu = self.builder.get_object("recentmenu")

    # update the file history list
    def update_history(self):
        # empty the history submenu
        def history_foreach(child):
            self.history_menu.remove(child)
        self.history_menu.foreach(history_foreach)
        # add files to history menu
        for file in self.file.history:
            menu_item = self.history_action.create_menu_item()
            try:
                menu_item.set_property('label', file)
            except TypeError:
                #print 'Your GTK library does not support labelling new menu items.'
                #print 'Please upgrade to version 2.16 or later.'
                menu_item.set_property('name', file)
            menu_item.connect('activate', self.history_callback)
            self.history_menu.append(menu_item)

    # history menu item click
    def history_callback(self, item, data=None):
        if item:
            file = ''
            try:
                file = item.get_property('label')
            except TypeError:
                file = item.get_property('name')
            allow_new = True
            if self.file.different:
                allow_new = False
                dialog = gtk.MessageDialog(self.window, 
                    gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                    gtk.MESSAGE_INFO, 
                    gtk.BUTTONS_YES_NO, 
                    'You have not saved your current document.\nContinue?')
                response = dialog.run()
                dialog.destroy()
                if response == gtk.RESPONSE_YES:
                    allow_new = True
            if allow_new:
                self.open_file(file)

    ''' BOOKMARKS '''
    # bookmarks init
    def create_bookmarks_gui(self):
        self.bookmarks_action = gtk.Action('Bookmarks', '_Bookmarks', None, None)
        self.bookmarks_menu = self.builder.get_object("bookmarksmenu")
        # add bookmark
        self.add_bookmark_menu_item = self.bookmarks_action.create_menu_item()
        try:
            self.add_bookmark_menu_item.set_property('label', '_Add Bookmark')
        except TypeError:
            print 'Your GTK library does not support labelling new menu items.'
            print 'Please upgrade to version 2.16 or later.'
            self.add_bookmark_menu_item.set_property('name', '_Add Bookmark')
        self.add_bookmark_menu_item.connect("activate", self.add_bookmark_callback)
        self.bookmarks_menu.append(self.add_bookmark_menu_item)
        # remove bookmark
        self.remove_bookmark_menu_item = self.bookmarks_action.create_menu_item()
        try:
            self.remove_bookmark_menu_item.set_property('label', '_Remove Bookmark')
        except TypeError:
            self.remove_bookmark_menu_item.set_property('name', '_Remove Bookmark')
        self.remove_bookmark_menu_item.connect("activate", self.remove_bookmark_callback)
        self.bookmarks_menu.append(self.remove_bookmark_menu_item)

    # update all bookmarks
    def update_bookmarks(self):
        # empty the bookmarks submenu
        def bookmarks_remove(child):
            label = child.get_property('label')
            if label != '_Add Bookmark' and label != '_Remove Bookmark':
                self.bookmarks_menu.remove(child)
        self.bookmarks_menu.foreach(bookmarks_remove)
        # add a separator
        seperator = gtk.SeparatorMenuItem()
        self.bookmarks_menu.append(seperator)
        seperator.set_property('visible', True)
        # now build the list
        count = 0
        for node_id in self.document.bookmarks:
            node = self.document.fetch_node_by_id(node_id)
            if node:
                count += 1
                menu_item = self.bookmarks_action.create_menu_item()
                try:
                    menu_item.set_property('label', '(_%d) %s' % (count, node.get_title_with_parent()))
                    menu_item.set_property('name', node.id)
                except TypeError:
                    menu_item.set_property('name', node.id)
                menu_item.connect('activate', self.bookmark_selection_callback)
                self.bookmarks_menu.append(menu_item)

    # add bookmark callback
    def add_bookmark_callback(self, data=None):
        if self.editor_node:
            self.add_bookmark(self.editor_node)
            self.update_bookmarks()
            self.update_tool_buttons()

    # remove bookmark callback
    def remove_bookmark_callback(self, data=None):
        if self.editor_node:
            self.remove_bookmark(self.editor_node)
            self.update_bookmarks()
            self.update_tool_buttons()

    # add bookmark
    def add_bookmark(self, node):
        if node:
            self.document.add_bookmark(node)

    # remove bookmark
    def remove_bookmark(self, node):
        if node:
            self.document.remove_bookmark(node)

    # user selects a bookmark from list
    def bookmark_selection_callback(self, item, data=None):
        if item:
            bookmark_id = int(item.get_property('name'))
            if bookmark_id >= 0:
                node = self.document.fetch_node_by_id(bookmark_id)
                if node:
                    if not self.notebook_switch_node(node):
                        self.find_iter_by_id(node.id)
                        if self.found:
                            self.add_to_notebook(node, self.found)
                            self.node_visit(node)
                    else:
                        self.node_visit(node)

    # is the current tab a bookmark
    def is_current_tab_a_bookmark(self):
        result = False
        if self.editor_node:
            result = self.document.is_node_bookmarked(self.editor_node)
        return result

    # click and edit the node title (F2)
    def edit_node_title(self):
        if self.editor_iter:
            path = self.treeview.get_model().get_path(self.editor_iter)
            self.treeview.expand_to_path(path)
            self.treeview.scroll_to_cell(path)
            #self.treeview.set_cursor(path, self.treeview.get_column(0), True)
            self.treeview.grab_focus()
            #e = gtk.gdk.Event(gtk.gdk.KEY_PRESS)
            #e.state = 0
            #e.keyval = 65293
            #e.hardware_keycode = 65293
            #e.window = self.window.get_property('frame')
            #e.time = 0
            #self.window.emit("key-press-event", e)

    # textview popup
    def textview_populate_popup_callback(self, textview, menu, userdata=None):
        if self.editor_node:
            if not self.editor_node.view and self.current_buffer.get_has_selection():
                separator = gtk.SeparatorMenuItem()
                menu.append(separator)
                menu_item = gtk.ImageMenuItem(gtk.STOCK_ADD)
                menu_item.set_property('label', 'Move Selected Text to New Child')
                menu_item.connect("activate", self.nodify_selected_text_callback)
                menu.append(menu_item)
                menu.show_all()

    # takes a chunk of text and pushes it into a new child node
    def nodify_selected_text_callback(self, widget, userdata=None):
        if not self.editor_node.view and self.current_buffer.get_has_selection():
            selection = self.current_buffer.get_selection_bounds()
            start = selection[0]
            end = selection[1]
            text = self.current_buffer.get_text(start, end)
            new = self.document.add_node_guess_title(self.editor_node, text)
            new_iter = self.add_document_node_to_tree(new, self.editor_iter)
            self.current_buffer.delete(start, end)
            if not self.row_expanded(self.editor_iter):
                self.expand_row(self.editor_iter)
            self.bump()
            self.update_tool_buttons()
            self.update_textview()
            self.update_attributes()
            self.update_tree_node_titles(self.editor_node)

    # treeview area popup
    def create_treeview_popup_menu(self):
        if self.editor_node:
            popup_menu = gtk.Menu()
            # common node functions
            menu_item = gtk.ImageMenuItem(gtk.STOCK_CONVERT)
            menu_item.set_property('label', 'Add _Child')
            menu_item.connect("activate", self.new_child_node_callback)
            popup_menu.append(menu_item)
            # document-node functions
            if self.editor_node != self.document:
                menu_item = gtk.ImageMenuItem(gtk.STOCK_ADD)
                menu_item.connect("activate", self.new_node_before_callback)
                menu_item.set_property('label', 'Add _Before')
                popup_menu.append(menu_item)
                menu_item = gtk.ImageMenuItem(gtk.STOCK_ADD)
                menu_item.set_property('label', 'Add _After')
                menu_item.connect("activate", self.new_node_after_callback)
                popup_menu.append(menu_item)
                if not self.document.is_a_first_node(self.editor_node):
                    menu_item = gtk.ImageMenuItem(gtk.STOCK_GO_UP)
                    menu_item.set_property('label', 'Move _Up')
                    menu_item.connect("activate", self.move_node_up_callback)
                    popup_menu.append(menu_item)
                if not self.document.is_a_last_node(self.editor_node):
                    menu_item = gtk.ImageMenuItem(gtk.STOCK_GO_DOWN)
                    menu_item.set_property('label', 'Move _Down')
                    menu_item.connect("activate", self.move_node_down_callback)
                    popup_menu.append(menu_item)
                if self.document.can_move_left(self.editor_node):
                    menu_item = gtk.ImageMenuItem(gtk.STOCK_GO_BACK)
                    menu_item.set_property('label', 'Move _Left')
                    menu_item.connect("activate", self.move_node_left_callback)
                    popup_menu.append(menu_item)
                if self.document.can_move_right(self.editor_node):
                    menu_item = gtk.ImageMenuItem(gtk.STOCK_GO_FORWARD)
                    menu_item.set_property('label', 'Move _Right')
                    menu_item.connect("activate", self.move_node_right_callback)
                    popup_menu.append(menu_item)
            if self.document.is_node_bookmarked(self.editor_node):
                menu_item = gtk.ImageMenuItem(gtk.STOCK_REMOVE)
                menu_item.set_property('label', 'Remove _Bookmark')
                menu_item.connect("activate", self.remove_bookmark_callback)
                popup_menu.append(menu_item)
            else:
                menu_item = gtk.ImageMenuItem(gtk.STOCK_ADD)
                menu_item.set_property('label', 'Add _Bookmark')
                menu_item.connect("activate", self.add_bookmark_callback)
                popup_menu.append(menu_item)
            if self.editor_node.has_children():
                menu_item = gtk.ImageMenuItem(gtk.STOCK_FULLSCREEN)
                menu_item.set_property('label', 'E_xpand All')
                menu_item.connect("activate", self.expand_all_children_callback)
                popup_menu.append(menu_item)
            if self.editor_node != self.document:
                menu_item = gtk.ImageMenuItem(gtk.STOCK_DELETE)
                menu_item.set_property('label', 'Remove')
                menu_item.connect("activate", self.remove_node_callback)
                popup_menu.append(menu_item)
            if self.editor_node.has_children():
                menu_item = gtk.ImageMenuItem(gtk.STOCK_UNDELETE)
                menu_item.set_property('label', 'Remove Children')
                menu_item.connect("activate", self.remove_children_callback)
                popup_menu.append(menu_item)
            return popup_menu
        else:
            return False

    # treeview mouse button press
    def treeview_button_press_callback(self, widget, event):
        # right click
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            path_info = self.treeview.get_path_at_pos(x, y)
            if path_info is not None:
                path, col, cellx, celly = path_info
                self.treeview.grab_focus()
                self.treeview.set_cursor(path, col, 0)
                if self.editor_node:
                    menu = self.create_treeview_popup_menu()
                    menu.show_all()
                    menu.popup( None, None, None, event.button, time)
            return True

    #checkbutton_statusbar
    def show_statusbar_callback(self, toggled, data=None): 
        menu_item = self.builder.get_object("checkmenuitem_statusbar")
        self.file.show_statusbar = menu_item.get_active()
        self.file.save_settings_default()
        self.update_settings()

    #checkmenuitem_toolbar_tree
    def show_toolbar_tree_callback(self, toggled, data=None): 
        menu_item = self.builder.get_object("checkmenuitem_toolbar_tree")
        self.file.show_toolbar_tree = menu_item.get_active()
        self.file.save_settings_default()
        self.update_settings()

    #checkmenuitem_toolbar_text
    def show_toolbar_text_callback(self, toggled, data=None): 
        menu_item = self.builder.get_object("checkmenuitem_toolbar_text")
        self.file.show_toolbar_text = menu_item.get_active()
        self.file.save_settings_default()
        self.update_settings()

    #checkmenuitem_spellcheck
    def checkbutton_spellcheck_callback(self, toggled, data=None): 
        if not editor.building_gui:
            menu_item = self.builder.get_object("checkmenuitem_spellcheck")
            self.file.spellcheck = menu_item.get_active()
            self.notify_spellcheck_change()

    #checkmenuitem_show_attributes
    def show_attributes_callback(self, toggled, data=None): 
        menu_item = self.builder.get_object("checkmenuitem_show_attributes")
        self.file.show_attributes = menu_item.get_active()
        self.file.save_settings_default()
        self.update_settings()

    # callback for statistics window
    def statistics_callback(self, data=None):
        new_statistics = True
        if self.statistics:
            if self.statistics.window and self.statistics.window.get_property('visible'):
                self.statistics.window.deiconify()
                self.statistics.window.show()
                self.statistics.window.set_keep_above(True)
                self.statistics.window.set_keep_above(False)
                new_statistics = False
        if new_statistics:
            self.statistics = KabikabooStatisticsWindow()
            self.statistics.set_data(self, self.file, self.document)
            self.statistics.window.show()

    # callback for import
    def import_text_callback(self, data=None):
        chooser = gtk.FileChooserDialog(title="Import Text File", parent=None, 
            action=gtk.FILE_CHOOSER_ACTION_OPEN,
            buttons=(gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN,gtk.RESPONSE_OK))
        chooser.set_default_response(gtk.RESPONSE_OK)
        filter = gtk.FileFilter()
        filter.set_name(".txt documents")
        filter.add_pattern("*.txt")
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("Kaboo documents")
        filter.add_pattern("*.kaboo")
        chooser.add_filter(filter)
        filter = gtk.FileFilter()
        filter.set_name("All files")
        filter.add_pattern("*")
        chooser.add_filter(filter)
        if self.file.last_import_directory != '':
            chooser.set_current_folder(self.file.last_import_directory)
        else:
            home = os.path.expanduser('~')
            chooser.set_filename(os.path.join(home, 'Documents'))
        response = chooser.run()

        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.import_text_file(filename, chooser)
            chooser.destroy()
        elif response == gtk.RESPONSE_CANCEL:
            chooser.destroy()

    # file handler
    def import_text_file(self, filename, dialog=None):
        result = self.file.import_text_file(filename, self.editor_node)
        if result:
            self.update_textview()
        else:
            dialog2 = gtk.MessageDialog(self.window, 
                gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT, 
                gtk.MESSAGE_INFO, 
                gtk.BUTTONS_OK, 
                'Error importing file.')
            response = dialog2.run()
            dialog2.destroy()
        return result

    # split node every one line break
    def split_node_one_callback(self, widget, userdata=None):
        if self.editor_node and self.editor_node.is_splittable():
            text = self.editor_node.text
            split = text.splitlines()
            for line in split:
                if line != '':
                    new = self.document.add_node_guess_title(self.editor_node, line)
                    new_iter = self.add_document_node_to_tree(new, self.editor_iter)
                    if not self.row_expanded(self.editor_iter):
                        self.expand_row(self.editor_iter)
            self.editor_node.set_text('')
            self.editor_node.view = True
            self.bump()
            self.update_tool_buttons()
            self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_attributes()

    # split node every two line breaks
    def split_node_two_callback(self, widget, userdata=None):
        if self.editor_node and self.editor_node.is_splittable():
            text = self.editor_node.text
            split = text.split("\n\n")
            for line in split:
                if line != '':
                    new = self.document.add_node_guess_title(self.editor_node, line)
                    new_iter = self.add_document_node_to_tree(new, self.editor_iter)
                    if not self.row_expanded(self.editor_iter):
                        self.expand_row(self.editor_iter)
            self.editor_node.set_text('')
            self.editor_node.view = True
            self.bump()
            self.update_tool_buttons()
            self.update_textview()
            self.update_tree_node_titles(self.editor_node)
            self.update_attributes()

    # copy children text with titles into parent
    def unify_with_callback(self, widget, userdata=None):
        if self.editor_node and self.editor_node.is_unifiable():
            self.editor_node.view = False
            self.editor_node.absorb_children_text(True)
            self.remove_children()
            self.bump()
            self.update_tool_buttons()
            self.update_textview()
            self.update_attributes()

    # copy children text without titles into parent
    def unify_without_callback(self, widget, userdata=None):
        if self.editor_node and self.editor_node.is_unifiable():
            self.editor_node.view = False
            self.editor_node.absorb_children_text(False)
            self.remove_children()
            self.bump()
            self.update_tool_buttons()
            self.update_textview()
            self.update_attributes()

    # fullscreen
    def fullscreen_switch(self, widget=None):
        if not self.file.fullscreen:
            self.window.fullscreen()
            self.file.fullscreen = True
        else:
            self.window.unfullscreen()
            self.file.fullscreen = False

    ''' TEXT EDITING (FONTS, TAGS) '''
    # text toolbar init
    def create_toolbar_text(self):
        self.toolbar_text = self.builder.get_object("toolbar_text")
        self.toolbar_text.set_style(gtk.TOOLBAR_ICONS)
        # bold
        self.bold_toolbutton = gtk.ToolButton(gtk.STOCK_BOLD)
        self.bold_toolbutton.set_label('Bold')
        self.bold_toolbutton.set_tooltip_text('Bold (Ctrl+B)')
        self.bold_toolbutton.connect('clicked', self.bold_callback)
        self.bold_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.bold_toolbutton, -1)
        # italic
        self.italic_toolbutton = gtk.ToolButton(gtk.STOCK_ITALIC)
        self.italic_toolbutton.set_label('Italic')
        self.italic_toolbutton.set_tooltip_text('Italic (Ctrl+I)')
        self.italic_toolbutton.connect('clicked', self.italic_callback)
        self.italic_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.italic_toolbutton, -1)
        # underline
        self.underline_toolbutton = gtk.ToolButton(gtk.STOCK_UNDERLINE)
        self.underline_toolbutton.set_label('Underline')
        self.underline_toolbutton.set_tooltip_text('Underline (Ctrl+U)')
        self.underline_toolbutton.connect('clicked', self.underline_callback)
        self.underline_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.underline_toolbutton, -1)
        # font
        self.font_toolbutton = gtk.ToolButton(gtk.STOCK_SELECT_FONT)
        self.font_toolbutton.set_label('Font')
        self.font_toolbutton.set_tooltip_text('Font')
        #self.font_toolbutton.connect('clicked', self.font_callback)
        self.font_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.font_toolbutton, -1)
        # increase size
        self.increase_toolbutton = gtk.ToolButton(gtk.STOCK_ADD)
        self.increase_toolbutton.set_label('Grow')
        self.increase_toolbutton.set_tooltip_text('Increase Text Size')
        #self.increase_toolbutton.connect('clicked', self.increase_callback)
        self.increase_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.increase_toolbutton, -1)
        # decrease size
        self.shrink_toolbutton = gtk.ToolButton(gtk.STOCK_REMOVE)
        self.shrink_toolbutton.set_label('Shrink')
        self.shrink_toolbutton.set_tooltip_text('Decrease Text Size')
        #self.shrink_toolbutton.connect('clicked', self.shrink_callback)
        self.shrink_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.shrink_toolbutton, -1)
        # fill justify
        self.fill_justify_toolbutton = gtk.ToolButton(gtk.STOCK_JUSTIFY_FILL)
        self.fill_justify_toolbutton.set_label('Fill Justify')
        self.fill_justify_toolbutton.set_tooltip_text('Fill Justify')
        #self.fill_justify_toolbutton.connect('clicked', self.fill_justify_callback)
        self.fill_justify_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.fill_justify_toolbutton, -1)
        # left justify
        self.left_justify_toolbutton = gtk.ToolButton(gtk.STOCK_JUSTIFY_LEFT)
        self.left_justify_toolbutton.set_label('Left Justify')
        self.left_justify_toolbutton.set_tooltip_text('Left Justify')
        #self.left_justify_toolbutton.connect('clicked', self.left_justify_callback)
        self.left_justify_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.left_justify_toolbutton, -1)
        # center justify
        self.center_justify_toolbutton = gtk.ToolButton(gtk.STOCK_JUSTIFY_CENTER)
        self.center_justify_toolbutton.set_label('Center Justify')
        self.center_justify_toolbutton.set_tooltip_text('Center Justify')
        #self.center_justify_toolbutton.connect('clicked', self.center_justify_callback)
        self.center_justify_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.center_justify_toolbutton, -1)
        # right justify
        self.right_justify_toolbutton = gtk.ToolButton(gtk.STOCK_JUSTIFY_RIGHT)
        self.right_justify_toolbutton.set_label('Right Justify')
        self.right_justify_toolbutton.set_tooltip_text('Right Justify')
        #self.right_justify_toolbutton.connect('clicked', self.right_justify_callback)
        self.right_justify_toolbutton.set_property('visible', True)
        self.toolbar_text.insert(self.right_justify_toolbutton, -1)

    # apply/remove tag
    def flip_tag_on_selection(self, tag_name):
        # find the selection range
        (start, end) = self.current_buffer.get_selection_bounds()
        # is it a valid range?
        if start >= 0 and end > 0 and start != end:
            # we need to get the tag from the buffer since we have multiple buffers
            tag = None
            has_start_tag = False
            has_end_tag = False
            # search for existing tag at start
            for search_tag in start.get_tags():
                if search_tag.get_property('name') == tag_name:
                    tag = search_tag
                    has_start_tag = True
            # search for existing tag at end
            for search_tag in end.get_tags():
                if search_tag.get_property('name') == tag_name:
                    tag = search_tag
                    has_end_tag = True
            # did we find a tag?
            if has_start_tag or has_end_tag:
                if (start.has_tag(tag) and end.has_tag(tag)) or (start.has_tag(tag) and end.ends_tag(tag)):
                    self.current_buffer.remove_tag(tag, start, end)
                else:
                    self.current_buffer.apply_tag_by_name(tag_name, start, end)
            else:
                self.current_buffer.apply_tag_by_name(tag_name, start, end)

    # bold
    def bold_callback(self, widget):
        if self.editor_node and not self.editor_node.view:
            self.flip_tag_on_selection('bold')

    # italic
    def italic_callback(self, widget):
        if self.editor_node and not self.editor_node.view:
            self.flip_tag_on_selection('italic')

    # unerline
    def underline_callback(self, widget):
        if self.editor_node and not self.editor_node.view:
            self.flip_tag_on_selection('underline')

    # check for duplicate instance of kabikaboo
    def check_for_duplicate_instance(self):
        result = False
        # WARNING: LINUX ONLY CODE
        output = commands.getoutput('ps -ax')
        # check for 2 or more regular instances
        if output.count('python src/kabikaboo.py') >= 2:
            result = True
        # check for instance and development instance
        if output.count('python src/kabikaboo.py') >= 1 and output.count('python -W ignore::DeprecationWarning src/kabikaboo.py') >= 1:
            result = True
        if result:
            print 'Duplicate instance of Kabikaboo already running.'
            print 'Will not open last file in this case.'
            print 'Starting with new document.'
            self.file.working_file = ''
        return result

    ''' SPELLCHECK '''
    # turn spellcheck on off
    def notify_spellcheck_change(self):
        # check all textviews
        for textview in self.book_textviews:
            # spellcheck is on
            if self.file.spellcheck:
                #check for existing spellcheck
                try:
                    spell = gtkspell.get_from_text_view(textview)
                except SystemError:
                    # none found, add one
                    gtkspell.Spell(textview)
            # spellcheck is off
            else:
                # check for existing spellcheck
                try:
                    spell = gtkspell.get_from_text_view(textview)
                    # one found, remove it
                    spell.detach()
                except SystemError:
                    pass

    def spellcheck_menu_item_toggle(self, widget=None):
        if not editor.building_gui:
            self.file.spellcheck = self.spellcheck_menu_item.get_active()
            self.file.save_settings_default()
            self.update_settings_window()
            self.notify_spellcheck_change()

    ''' RECENTLY VISITED '''
    # visited init
    def create_visited_gui(self):
        # visited
        self.visited_action = gtk.Action('Visits', '_Visits', None, None)
        self.visited_menu = self.builder.get_object("visitsmenu")
        # recently visited
        self.visited_recent_menuitem = self.visited_action.create_menu_item()
        try:
            self.visited_recent_menuitem.set_property('label', '_Recent')
        except TypeError:
            self.visited_recent_menuitem.set_property('name', '_Recent')
        self.visited_menu.append(self.visited_recent_menuitem)
        self.visited_recent_menu = gtk.Menu()
        self.visited_recent_menuitem.set_submenu(self.visited_recent_menu)
        self.visited_recent_menuitem.connect('activate', self.menuitem_visited_recent_callback)
        # session visited
        self.visited_session_menuitem = self.visited_action.create_menu_item()
        try:
            self.visited_session_menuitem.set_property('label', '_Session')
        except TypeError:
            self.visited_session_menuitem.set_property('name', '_Session')
        self.visited_menu.append(self.visited_session_menuitem)
        self.visited_session_menu = gtk.Menu()
        self.visited_session_menuitem.set_submenu(self.visited_session_menu)
        self.visited_session_menuitem.connect('activate', self.menuitem_visited_session_callback)
        # all visited
        self.visited_all_menuitem = self.visited_action.create_menu_item()
        try:
            self.visited_all_menuitem.set_property('label', '_All')
        except TypeError:
            self.visited_all_menuitem.set_property('name', '_All')
        self.visited_menu.append(self.visited_all_menuitem)
        self.visited_all_menu = gtk.Menu()
        self.visited_all_menuitem.set_submenu(self.visited_all_menu)
        self.visited_all_menuitem.connect('activate', self.menuitem_visited_all_callback)

    # user selects a visited from list
    def visited_selection_callback(self, item, data=None):
        if item:
            visited_id = int(item.get_property('name'))
            if visited_id >= 0:
                node = self.document.fetch_node_by_id(visited_id)
                if node:
                    if not self.notebook_switch_node(node):
                        self.find_iter_by_id(node.id)
                        if self.found:
                            self.add_to_notebook(node, self.found)
                            self.node_visit(node)
                    else:
                        self.node_visit(node)

    # node visit
    def node_visit(self, node):
        if node:
            self.document.visit(node)

    # when user hovers over "Visited->Recent"
    def menuitem_visited_recent_callback(self, menuitem):
        self.update_recently_visited()

    # when user hovers over "Visited->Session"
    def menuitem_visited_session_callback(self, menuitem):
        self.update_session_visited()

    # when user hovers over "Visited->All"
    def menuitem_visited_all_callback(self, menuitem):
        self.update_all_visited()

    # update recently visited menu
    def update_recently_visited(self):
        # empty the visited submenus
        def visited_remove(child):
            self.visited_recent_menu.remove(child)
        self.visited_recent_menu.foreach(visited_remove)
        # now build the list
        count = 0
        for node_id in self.document.visited:
            node = self.document.fetch_node_by_id(node_id)
            if node:
                count += 1
                menu_item = gtk.MenuItem()
                try:
                    menu_item.set_property('label', '%s' % (node.get_title_with_parent()))
                    menu_item.set_property('name', node.id)
                except TypeError:
                    menu_item.set_property('name', node.id)
                menu_item.connect('activate', self.visited_selection_callback)
                self.visited_recent_menu.append(menu_item)
        self.visited_recent_menu.show_all()

    # update session visited menu
    def update_session_visited(self):
        # empty the visited submenus
        def visited_remove(child):
            self.visited_session_menu.remove(child)
        self.visited_session_menu.foreach(visited_remove)
        # now build the list
        count = 0
        visited = self.document.get_visited_sessions_list()
        for node in visited:
            count += 1
            menu_item = gtk.MenuItem()
            try:
                menu_item.set_property('label', '%s (%d)' % (node.get_title_with_parent(), node.visits_session))
                menu_item.set_property('name', node.id)
            except TypeError:
                menu_item.set_property('name', node.id)
            menu_item.connect('activate', self.visited_selection_callback)
            self.visited_session_menu.append(menu_item)
        self.visited_session_menu.show_all()

    # update all visited menu
    def update_all_visited(self):
        # empty the visited submenus
        def visited_remove(child):
            self.visited_all_menu.remove(child)
        self.visited_all_menu.foreach(visited_remove)
        # now build the list
        count = 0
        visited = self.document.get_visited_all_list()
        for node in visited:
            count += 1
            menu_item = gtk.MenuItem()
            try:
                menu_item.set_property('label', '%s (%d)' % (node.get_title_with_parent(), node.visits_all))
                menu_item.set_property('name', node.id)
            except TypeError:
                menu_item.set_property('name', node.id)
            menu_item.connect('activate', self.visited_selection_callback)
            self.visited_all_menu.append(menu_item)
        self.visited_all_menu.show_all()

    # autosave
    def autosave(self):
        if self.file.autosave:
            if self.file.working_file != '' and self.file.different:
                if self.file.autosave_version:
                    self.save_version()
                else:
                    self.file.save(self.document)
                    self.unbump()
                    self.update_history()
                    self.update_status_bar()
            return True
        else:
            return False

    # check and apply autosave settings
    def check_autosave(self):
        # remove existing autosave timers
        if self.autosave_id > -1:
            glib.source_remove(self.autosave_id)
            self.autosave_id = -1
        # add autosave timer
        if self.file.autosave:
            # enable autosave
            self.autosave_id = glib.timeout_add_seconds(60*int(self.file.autosave_interval), self.autosave)
            # the next timeout call will stop when autosave() returns false
   
    # check and apply spaces above the line in the editor
    def check_spaces_above(self):
       self.current_textview.set_pixels_above_lines(self.file.spaces_above)
       self.update_textview()
   
   # check and apply spaces above the line in the editor
    def check_spaces_below(self):
        self.current_textview.set_pixels_below_lines(self.file.spaces_below)
        self.update_textview()
#
# ''' MAIN PROGRAM LOOP '''
#
if __name__ == "__main__":
    # Init Step 1: create our first window
    editor = KabikabooMainWindow()
    # building gui
    editor.building_gui = True
    # Init Step 2: initialize the GUI with values
    editor.initialize_interface()
    # Init Step 3: populate the GUI with data
    editor.populate_interface()
    # Init Step 4: show the window now
    editor.window_show()
    # Init Step 5: do some tricks after the window is shown
    editor.post_window_show()
    # done building gui
    editor.building_gui = False
    # run gtk loop until close
    gtk.main()
    # after loop exits, save settings
    editor.file.save_settings_default()
    # save recovery file
    editor.file.save_recovery(True)
