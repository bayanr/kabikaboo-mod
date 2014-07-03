# Kabikaboo document
#
# Novel Writing Assistance Software
# Copyleft (c) 2009
# Created by David Kerr
# Naturally Intelligent Inc.
#
# Free and Open Source
# Licensed under GPL v2 or later
# No Warranty

def current_version():
    return '1.7'

# a list of node children
class KabikabooNodeList:
    # init
    def __init__(self, owner):
        self.parent = owner
        self.list = []
    # create a node, simple wrapper5
    def create_node(self, owner, id):
        new_node = KabikabooNode(owner, id)
        self.list.append(new_node)
        return new_node
    # insert a node, simple wrapper
    def insert_node(self, owner, id, index):
        new_node = KabikabooNode(owner, id)
        self.list.insert(index, new_node)
        return new_node
    # delete a node, simple wrapper
    def delete_node(self, node):
        self.list.remove(node)
    # find index of node
    def index_of_node(self, node):
        index = self.list.index(node)
        return index
    # clear nodes
    def clear_nodes(self):
        self.list = []
    # swap two nodes
    def swap(self, node, swap_node):
        result = False
        index1 = self.list.index(node)
        index2 = self.list.index(swap_node)
        if index1 != -1 and index2 != -1:
            self.list.remove(node)
            self.list.insert(index2, node)
        return result

# this is a text node in a Kabikaboo document
# each node has a list of 0..N children nodes
class KabikabooNode:
    BULLETING_NONE = 0
    BULLETING_NUMBER = 1
    BULLETING_ALPHA_LOWER = 2
    BULLETING_ALPHA = 3
    BULLETING_ALPHA_UPPER = 3
    BULLETING_ROMAN_LOWER = 4
    BULLETING_ROMAN_UPPER = 5
    BULLETING_DASH = 6
    BULLETING_DOT = 7
    # init
    def __init__(self, owner, id):
        self.id = id
        self.parent = owner
        self.children = KabikabooNodeList(self)
        self.title = 'Kabikaboo'
        self.text = ''
        self.view = False
        self.all = True
        self.bulleting = KabikabooNode.BULLETING_NONE
        self.visits_all = 0
        self.visits_session = 0
    # get title
    def get_title(self):
        return self.get_title_bullet() + self.title
    # get title bullet prefix
    def get_title_bullet(self):
        bullet = ''
        # int_to_roman from http://code.activestate.com/recipes/81611/
        def int_to_roman(input):
            if type(input) != type(1):
                raise TypeError, "expected integer, got %s" % type(input)
            if not 0 < input < 4000:
                raise ValueError, "Argument must be between 1 and 3999"   
            ints = (1000, 900,  500, 400, 100,  90, 50,  40, 10,  9,   5,  4,   1)
            nums = ('M',  'CM', 'D', 'CD','C', 'XC','L','XL','X','IX','V','IV','I')
            result = ""
            for i in range(len(ints)):
                count = int(input / ints[i])
                result += nums[i] * count
                input -= ints[i] * count
            return result
        if self.parent and self.parent.bulleting != KabikabooNode.BULLETING_NONE:
            if self.parent.bulleting == KabikabooNode.BULLETING_NUMBER:
                bullet = str(self.parent.children.index_of_node(self)+1) + '. '
            if self.parent.bulleting == KabikabooNode.BULLETING_ALPHA_UPPER:
                index = self.parent.children.index_of_node(self)
                myrep = int(index / 26)
                mystring = ''
                mychar = chr(index%26+65)
                bullet = chr((self.parent.children.index_of_node(self))%26+65) + '. '
            if self.parent.bulleting == KabikabooNode.BULLETING_ALPHA_LOWER:
                bullet = chr((self.parent.children.index_of_node(self))%26+97) + '. '
            if self.parent.bulleting == KabikabooNode.BULLETING_ROMAN_UPPER:
                bullet = int_to_roman(self.parent.children.index_of_node(self)+1) + '. '
            if self.parent.bulleting == KabikabooNode.BULLETING_ROMAN_LOWER:
                bullet = int_to_roman(self.parent.children.index_of_node(self)+1).lower() + '. '
        return bullet
    # set title
    def set_title(self, title):
        self.title = title
    # get text
    def get_text(self):
        return self.text
    # set text
    def set_text(self, text):
        self.text = text
    # add a child
    def add_child(self, id):
        node = self.children.create_node(self, id)
        node.parent = self
        return node
    # add a child
    def add_child(self, id, title, text):
        node = self.children.create_node(self, id)
        node.parent = self
        node.title = title
        node.text = text
        return node
    # insert a child
    def insert_child(self, id, index, title, text):
        node = self.children.insert_node(self, id, index)
        node.parent = self
        node.title = title
        node.text = text
        return node
    # return children
    def get_children(self):
        return self.children
    # has children
    def has_children(self):
        result = False
        if len(self.children.list) > 0:
            result = True
        return result
    #export text file
    def export_text(self, title, recurse, show_titles):
        text = ''
        if title:
            title = title + ' -> ' + self.get_title()
        else:
            title = self.get_title()
        if show_titles:
            text = title
            text +=  '\n'
            text +=  '-' * 2 * len(title)
            text +=  '\n'
        if(self.text):
            text +=  self.text
            text +=  '\n'
            text +=  '\n'
        if recurse:
            for child in self.children.list:
                text = text + child.export_text(title, recurse, show_titles)
        return text
    # view markuped text recursion
    def html_text(self, recurse, show_titles):
        text = '<html>\n'
        text += '<head>\n'
        text += '<title>' + self.get_title() + '</title>\n'
        text += '</head>\n'
        text += '<body>\n'
        text += self.html_text_node('', recurse, show_titles)
        text += '</body>\n'
        text += '</html>\n'
        return text
    # view markuped text recursion
    def html_text_node(self, title, recurse, show_titles):
        text = ''
        if show_titles:
            text = '<b>' + self.get_title() + '</b><br/>\n'
            if title:
                title += ' -> ' + self.get_title()
                text  += '<small>' + title + '</small><br/>\n'
            else:
                title = self.get_title()
            text +=  '-' * 2 * len(title)
            text +=  '<br/><br/>\n'
        if(self.text):
            text +=  self.text.replace('\n', '<br/>')
            text +=  '<br/>\n'
            text +=  '<br/>\n'
        if recurse:
            for child in self.children.list:
                text = text + child.html_text_node(title, recurse, show_titles)
        return text
    # get text to display
    def get_view_text(self, show_titles):
        if not self.view:
            return self.text
        else:
            return self.export_text('', self.all, show_titles)
    # get spaced title
    def get_spaced_title(self, length):
        return self.title.center(length, ' ')
    # get spaced title with bullets
    def get_spaced_bullet_title(self, length):
        title = self.get_title() 
        return title.center(length, ' ')
    # get recursive title with path
    def get_recursive_title(self, title = '', separator = ' -> '):
        title = self.get_title()
        if self.parent:
            title = self.parent.get_recursive_title(title, separator) + separator + title
        return title
    # get title with parent
    def get_title_with_parent(self):
        title = self.title
        if self.parent:
            title = self.parent.title + ' -> ' + title
        return title
    # get bulleting
    def get_bulleting(self):
        return self.bulleting
    # set bulleting
    def set_bulleting(self, bulleting):
        self.bulleting = bulleting
    # add bulleting
    def add_bulleting(self):
        self.bulleting = KabikabooNode.BULLETING_NONE
        for child in self.children.list:
            child.add_bulleting()
    # simple word count
    def word_count(self, recurse=True):
        words = self.text.split(None)
        word_count = len(words)
        if recurse:
            for child in self.children.list:
                word_count += child.word_count()
        return word_count
    # visible word count
    def visible_word_count(self, recurse=True):
        if not self.view:
            return self.word_count(recurse)
        else:
            text = self.export_text('', self.all, False)
            words = text.split(None)
            return len(words)
    # is this node splittable?
    def is_splittable(self):
        result = True
        if self.view:
            result = False
        if self.text == '':
            result = False
        return result
    # is this node unifiable?
    def is_unifiable(self):
        result = False
        if self.has_children():
            result = True
        return result
    # copy the children's text into this node
    def absorb_children_text(self, include_titles):
        for child in self.children.list:
            child.absorb_children_text(include_titles)
            if child.text != '' and child.title != '' and self.text != '':
                self.text += "\n\n"
            if include_titles and child.title != '':
                self.text += child.title
                self.text += "\n"
            if child.text != '':
                self.text += child.text
    # clear session visits
    def clear_session_visits(self):
        self.visits_session = 0
        for child in self.children.list:
            child.clear_session_visits()
    # add visit counters (for upgrade)
    def add_visit_counters(self):
        self.visits_all = 0
        self.visits_session = 0
        for child in self.children.list:
            child.add_visit_counters()
    # create a sorted visit list
    def add_to_session_visit_list(self, list, max):
        added = False
        if self.visits_session > 0:
            count = 0
            for node in list:
                if self.visits_session > node.visits_session:
                    list.insert(count, self)
                    added = True
                    break
                count = count + 1
            if not added and count < max:
                list.append(self)
                added = True
        if added:
            while len(list) > max:
                del list[len(list)-1]
        for child in self.children.list:
            child.add_to_session_visit_list(list, max)
    # create a sorted visit list
    def add_to_all_visit_list(self, list, max):
        added = False
        if self.visits_all > 0:
            count = 0
            for node in list:
                if self.visits_all > node.visits_all:
                    list.insert(count, self)
                    added = True
                    break
                count = count + 1
            if not added and count < max:
                list.append(self)
                added = True
        if added:
            while len(list) > max:
                del list[len(list)-1]
        for child in self.children.list:
            child.add_to_all_visit_list(list, max)

# top level node
class KabikabooDocument(KabikabooNode):
    # initialize
    def __init__(self):
        # unique id counter
        self.id = 0
        self.unique_id = 0
        # inherited init, using counter for id
        KabikabooNode.__init__(self, self.id, self.unique_id)
        # initialize data
        self.title = 'New Document'
        self.table = {}
        self.text = ''
        self.view = True
        # version 1.1
        self.tabs = []
        self.tab_max = 7
        self.version = current_version()
        # version 1.5
        self.bookmarks = []
        self.bookmark_max = 10
        self.show_titles_in_view = True
        self.show_titles_in_export = True
        # version 1.7 (recently visited nodes)
        self.visited = []
        self.visited_max = 10
        # add self to the table reference list
        self.table[self.id] = self
    # add node (always use this instead of node.add_child)
    def add_node(self, node, title, text):
        # increment the unique id counter
        self.unique_id = self.unique_id + 1
        # add the node into the tree
        new = node.add_child(self.unique_id, title, text)
        # also add this to the table, for reference by id
        self.table[new.id] = new
        # send result back
        return new
    # add node, and guess the title using the text
    def add_node_guess_title(self, node, text):
        # guess the title (get the first five words)
        title = ''
        lines = text.splitlines()
        goodline = ''
        for line in lines:
            if line != '' and line != ' ' and line != '\n':
                goodline = line
                break
        if goodline:
            sentence = goodline.split(' ')
            words = 0
            for word in sentence:
                if word != '' and word != ' ':
                    if words >= 1:
                        title += ' '
                    title += word
                    words += 1
                if words >= 5:
                    title += ' ...'
                    break
        if title == '':
            title = 'split'
        # get the new node
        new = self.add_node(node, title, text)
        # send result back
        return new
    # add node before another node, on the same level
    def add_node_before(self, node, title, text):
        index = self.find_index_of_node(node)
        new = None
        if index != -1:
            # increment the unique id counter
            self.unique_id = self.unique_id + 1
            # add the node into the tree
            new = node.parent.insert_child(self.unique_id, index, title, text)
            # also add this to the table, for reference by id
            self.table[new.id] = new
        return new
    #add node before another node, on the same level
    def add_node_after(self, node, title, text):
        index = self.find_index_of_node(node)
        new = None
        if index != -1:
            # move this index down one (after)
            index = index + 1
            # increment the unique id counter
            self.unique_id = self.unique_id + 1
            # add the node into the tree
            new = node.parent.insert_child(self.unique_id, index, title, text)
            # also add this to the table, for reference by id
            self.table[new.id] = new
        return new
    # find a node by id
    def valid_id(self, id):
        result = False
        if self.table[id] != None:
            result = True
        return result
    # find index of node
    def find_index_of_node(self, node):
        index = -1
        if(node.parent):
            index = node.parent.children.index_of_node(node)
        return index
    # first node?
    def is_a_first_node(self, node):
        index = -1
        if(node.parent):
            index = node.parent.children.index_of_node(node)
        return index == 0
    # last node?
    def is_a_last_node(self, node):
        index = -1
        if(node.parent):
            index = node.parent.children.index_of_node(node)
        return index == len(node.parent.children.list) - 1
    # can move up?
    def can_move_up(self, node):
        result = False
        if not self.is_a_first_node(node) and not node.id == self.id:
            result = True
        return result
    # can move down?
    def can_move_down(self, node):
        result = False
        if not self.is_a_last_node(node) and not node.id == self.id:
            result = True
        return result
    # can move left?
    def can_move_left(self, node):
        result = False
        if node.parent:
            if node.parent != self:
                result = True
        return result
    # can move right?
    def can_move_right(self, node):
        result = False
        if node != self:
            if not self.is_a_first_node(node):
                result = True
        return result
    # get move down node
    def get_move_down_node(self, node):
        return self.get_node_after(node)
    # get move up node
    def get_move_up_node(self, node):
        return self.get_node_before(node)
    # move down
    def move_node_down(self, node):
        result = False
        if self.can_move_down(node):
            swap_node = self.get_move_down_node(node)
            node.parent.children.swap(node, swap_node)
            result = True
        return result
    # move up
    def move_node_up(self, node):
        result = False
        if self.can_move_up(node):
            swap_node = self.get_move_up_node(node)
            node.parent.children.swap(node, swap_node)
            result = True
        return result
    # move left (to parents node after)
    def move_node_left(self, node):
        result = False
        #if not node.id == self.id and not node.parent == self.id:
        if self.can_move_left(node):
            new_index = self.find_index_of_node(node.parent) + 1
            new_parent = node.parent.parent
            node.parent.children.delete_node(node)
            new_parent.children.list.insert(new_index, node)
            node.parent = new_parent
            result = True
        return result
    # move right (to end of node befores children)
    def move_node_right(self, node):
        result = False
        if self.can_move_right(node):
            new_parent = self.get_node_before(node)
            node.parent.children.delete_node(node)
            new_parent.children.list.append(node)
            node.parent = new_parent
            result = True
        return result
    # return node after
    def get_node_after(self, node):
        return node.parent.children.list[node.parent.children.index_of_node(node) + 1]
    # return node before
    def get_node_before(self, node):
        return node.parent.children.list[node.parent.children.index_of_node(node) - 1]
    # find a node by id
    def fetch_node_by_id(self, id):
        if id in self.table:
            node = self.table[id]
        else:
            node = None
        return node
    # remove a node
    def remove_node(self, node):
        result = False
        # we can't delete the document node
        if node.id != self.id:
            # remove children
            for child in node.children.list:
                self.remove_node(child)
            # remove node from table
            self.table[node.id] = None
            # remove the node from the parents list
            node.parent.children.delete_node(node)
            # remove from tabs if in there
            self.remove_tab(node)
            # remove from bookmarks if in there
            self.remove_bookmark(node)
            # remove from visited if in there
            self.remove_visited(node)
            # success
            result = True
        return result
    # remove children
    def remove_children(self, node):
        result = False
        # remove children
        for child in reversed(node.children.list):
            self.remove_children(child)
            # we can't delete the document node
            if child.id != self.id:
                self.remove_node(child)
        # success
        result = True
        return result
    # clear this document
    def new_document(self):
        self.children.clear_nodes()
        self.table = {}
        self.id = 0
        self.unique_id = 0
        self.table[self.id] = self
        self.title = 'New Document'
        self.text = ''
        self.tabs = []
        self.tab_max = 7
        self.version = current_version()
    # populate for testing
    def generate_default_data(self):
        self.title = 'Kabikaboo'
        self.text = 'Welcome to Kabikaboo Recursive Writing Assistant!\nThis is sample data to show the capabilities of Kabikaboo.\nYou should create your own New Document from the File Menu.'
        self.view = False
    # check max tab, drop oldest
    # populate for testing
    def generate_test_data(self):
        self.generate_default_data()
        self.tab_max = 5
        self.add_tab(self)
        node = self.add_node(self, 'Plot', 'Plot Text ' * 32)
        node.bulleting = KabikabooNode.BULLETING_ALPHA_UPPER
        node.view = True
        node_act = self.add_node(node, 'Act One', ('Act One Text ' * 24 + '\n') * 4)
        self.add_bookmark(node_act)
        node_act = self.add_node(node, 'Act Two', ('Act Two Text ' * 48 + '\n') * 8)
        self.add_bookmark(node_act)
        node_act = self.add_node(node, 'Act Three', ('Act Three Text ' * 32 + '\n') * 2)
        self.add_bookmark(node_act)
        node2 = self.add_node(self, 'Characters', '')
        node2.view = True
        node2.bulleting = KabikabooNode.BULLETING_NUMBER
        node = self.add_node(node2, 'Primary', '')
        node.view = True
        node.bulleting = KabikabooNode.BULLETING_ROMAN_UPPER
        node3 = self.add_node(node, 'Protagonist', 'Protagonist Description ' * 32)
        self.add_bookmark(node3)
        node3.bulleting = KabikabooNode.BULLETING_ALPHA_LOWER
        self.add_node(node3, 'Background', 'Background Information ' * 16)
        self.add_node(node3, 'Quotes', 'Memorable Quotes ' * 16)
        self.add_node(node3, 'Research', 'Research Area ' * 16)
        node3 = self.add_node(node, 'Antagonist', 'Antagonist Description ' * 32)
        node3.bulleting = KabikabooNode.BULLETING_ALPHA_LOWER
        self.add_node(node3, 'Background', 'Background Information ' * 16)
        self.add_node(node3, 'Quotes', 'Memorable Quotes ' * 16)
        self.add_node(node3, 'Research', 'Research Area ' * 16)
        node = self.add_node(node2, 'Secondary', '')
        node.view = True
        node.bulleting = KabikabooNode.BULLETING_ROMAN_LOWER
        self.add_node(node, 'Mom', 'Mom Description ' * 24)
        self.add_node(node, 'Dad', 'Dad Description ' * 24)
        node = self.add_node(self, 'Events', 'Events Text ' * 16)
        node.view = True
        self.add_node(node, 'Past', 'Past Text ' * 96)
        self.add_node(node, 'Present', 'Present Text ' * 96)
        self.add_node(node, 'Future', 'Future Text ' * 96)
        node = self.add_node(self, 'Locations', 'Location Text ' * 16)
        node.view = True
        self.add_node(node, 'Starting Location', 'Starting Location Text ' * 64)
        self.add_node(node, 'Middle Location', 'Middle Location Text ' * 64)
        self.add_node(node, 'Final Location', 'Final Location Text ' * 64)
        node = self.add_node(self, 'Culture', 'Culture Text ' * 16)
        node.view = True
        self.add_node(node, 'Art', 'Art Text ' * 128)
        self.add_node(node, 'Music', 'Music Text ' * 128)
        self.add_node(node, 'Norms', 'Norms Text ' * 128)

    # TABS (list of recently viewed nodes)
    # add tab
    def add_tab(self, node):
        added = False
        changed = False
        moved = False
        duplicate = False
        overflow = False
        previousIndex = -1
        newIndex = -1
        # check if the tab is already in the list, remove it (will be readded at front)
        if node.id in self.tabs:
            duplicate = True
            if self.tabs.index(node.id) > 0:
                previousIndex = self.tabs.index(node.id)
                self.tabs.remove(node.id)
                self.tabs.insert(0, node.id)
                newIndex = 0
                moved = True
                changed = True
        # add the tab
        if not duplicate:
            self.tabs.insert(0, node.id)
            added = True
            changed = True
        if self.check_tab_overflow():
            changed = True
            overflow = True
        return added, moved, changed, duplicate, overflow, previousIndex, newIndex

    # check tab overflow
    def check_tab_overflow(self):
        result = False
        while(len(self.tabs) > self.tab_max):
            self.tabs.remove(self.tabs[len(self.tabs)-1])
            result = True
        return result

    # remove tab
    def remove_tab(self, node):
        if node.id in self.tabs:
            self.tabs.remove(node.id)

    # remove tab
    def remove_last_tab(self):
        if len(self.tabs) > 0:
            node_id = self.tabs[len(self.tabs)-1]
            if node_id:
                self.tabs.remove(node_id)

    # add bookmark
    def add_bookmark(self, node):
        added = False
        changed = False
        moved = False
        duplicate = False
        overflow = False
        previousIndex = -1
        newIndex = -1
        # check if the bookmark is already in the list, remove it (will be readded at front)
        if node.id in self.bookmarks:
            duplicate = True
            if self.bookmarks.index(node.id) > 0:
                previousIndex = self.bookmarks.index(node.id)
                self.bookmarks.remove(node.id)
                self.bookmarks.insert(0, node.id)
                newIndex = 0
                moved = True
                changed = True
        # add the bookmark
        if not duplicate:
            self.bookmarks.insert(0, node.id)
            added = True
            changed = True
        if self.check_bookmark_overflow():
            changed = True
            overflow = True
        return added, moved, changed, duplicate, overflow, previousIndex, newIndex

    # remove bookmark
    def remove_bookmark(self, node):
        if node.id in self.bookmarks:
            self.bookmarks.remove(node.id)

    # check for bookmark overflow
    def check_bookmark_overflow(self):
        result = False
        while(len(self.bookmarks) > self.bookmark_max):
            self.bookmarks.remove(self.bookmarks[len(self.bookmarks)-1])
            result = True
        return result
        
    # check node in bookmarks
    def is_node_bookmarked(self, node):
        result = False
        for node_id in self.bookmarks:
            if node_id == node.id:
                result = True
        return result

    # add visited
    def add_visited(self, node):
        added = False
        changed = False
        moved = False
        duplicate = False
        overflow = False
        previousIndex = -1
        newIndex = -1
        # check if the visited is already in the list, remove it (will be readded at front)
        if node.id in self.visited:
            duplicate = True
            if self.visited.index(node.id) > 0:
                previousIndex = self.visited.index(node.id)
                self.visited.remove(node.id)
                self.visited.insert(0, node.id)
                newIndex = 0
                moved = True
                changed = True
        # add the visited
        if not duplicate:
            self.visited.insert(0, node.id)
            added = True
            changed = True
        if self.check_visited_overflow():
            changed = True
            overflow = True
        return added, moved, changed, duplicate, overflow, previousIndex, newIndex

    # remove visited
    def remove_visited(self, node):
        if node.id in self.visited:
            self.visited.remove(node.id)

    # check for visited overflow
    def check_visited_overflow(self):
        result = False
        while(len(self.visited) > self.visited_max):
            self.visited.remove(self.visited[len(self.visited)-1])
            result = True
        return result

    # visit a node
    def visit(self, node):
        if node:
            node.visits_all = node.visits_all + 1
            node.visits_session = node.visits_session + 1
            (added, moved, changed, duplicate, overflow, previousIndex, newIndex) = self.add_visited(node)
            return changed
        return False

    # clear visits
    def clear_recent_visits(self):
        self.visited = []

    # for upgrading to v1.7
    def add_visits_data(self):
        self.visited = []
        self.visited_max = 10
        self.add_visit_counters()

    # get the sorted list of session visits
    def get_visited_sessions_list(self):
        visited = []
        self.add_to_session_visit_list(visited, self.visited_max)
        return visited

    # get the sorted list of all visits
    def get_visited_all_list(self):
        visited = []
        self.add_to_all_visit_list(visited, self.visited_max)
        return visited

    # should call this after loading a document from file
    def post_load(self):
        # clear visits this session
        # this cant be done on save, because then it would be cleared from users session
        #  should really be stored in application but oh well
        self.clear_session_visits()
        # add first node in tabs to session visit
        if len(self.tabs) > 0:
            node_id = self.tabs[0]
            node = self.fetch_node_by_id(node_id)
            if node:
                # session
                node.visits_session = 1
                # all
                if node.visits_all == 0:
                    node.visits_all = 1
                # recent
                self.add_visited(node)

