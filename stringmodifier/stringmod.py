# -*- coding: utf-8 -*-
#
#  String Modifiers plugin for gedit
#
#  Copyright (C) 2010, Hertatijanto Hartono <dvertx@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330,
#  Boston, MA 02111-1307, USA.

"""
2010-12-01  Version 1.0

This module provides the main plugin object which interacts with gedit.

See __init__.py for plugin's description.

Classes:
StringModPlugin
StringModWindowHelper

"""

import os
import re
import gtk
import gedit
from gettext import gettext as _

from strmodconf import StringModConfigHelper

# Menu items
ui_str = """
<ui>
  <menubar name="MenuBar">
    <menu name="ToolsMenu" action="Tools">
      <placeholder name="ToolsOps_2">
        <menu action="StringMod">
         <menuitem name="Braces" action="Braces"/>
         <menuitem name="Brackets" action="Brackets"/>
         <menuitem name="Quotes" action="Quotes"/>
         <menuitem name="Custom" action="Custom"/>
         <separator/>
         <menuitem name="Str2CharArray" action="Str2CharArray"/>
         <menuitem name="Str2WordArray" action="Str2WordArray"/>
         <separator/>
         <menuitem name="Config" action="Config"/>
        </menu>
      </placeholder>
    </menu>
  </menubar>
</ui>
"""

class StringModWindowHelper:
    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin
        self.options = StringModConfigHelper.options
        self.encl_char = StringModConfigHelper.encl_char

        # Insert menu items
        self._insert_menu()

    def deactivate(self):
        # Remove any installed menu items
        self._remove_menu()

        self._window = None
        self._plugin = None
        self._action_group = None

    def _insert_menu(self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()

        # Create a new action group
        self._action_group = gtk.ActionGroup("StringModPluginActions")
        self._action_group.add_actions([("StringMod", None, _("String Modifiers")),
            ("Braces", None, _("Add curly braces"), self.options[0],
                _("Add enclosing curly braces to selected text"), self.on_encl_braces_activate),
            ("Brackets", None, _("Add brackets"), self.options[1],
                _("Add enclosing brackets to selected text"), self.on_encl_brackets_activate),
            ("Quotes", None, _("Add quotes"), self.options[2],
                _("Add enclosing quotes to selected text"), self.on_encl_quotes_activate),
            ("Custom", None, _("Add custom encl."), self.options[3],
                _("Add custom enclosing chars to selected text"), self.on_encl_custom_activate),
            ("Str2CharArray", None, _("String to char array"), self.options[4],
                _("Modify selected text into array of characters"), self.on_make_array_activate),
            ("Str2WordArray", None, _("String to word array"), self.options[5],
                _("Modify selected text into an array of words"), self.on_make_word_array_activate),
            ("Config", None, _("Configure..."), None,
                _("Configure String Modifiers"), self.on_configure_activate)])

        # Insert the action group
        manager.insert_action_group(self._action_group, -1)

        # Merge the UI
        self._ui_id = manager.add_ui_from_string(ui_str)

    def _remove_menu(self):
        # Get the GtkUIManager
        manager = self._window.get_ui_manager()

        # Remove the ui
        manager.remove_ui(self._ui_id)

        # Remove the action group
        manager.remove_action_group(self._action_group)

        # Make sure the manager updates
        manager.ensure_update()

    def update_ui(self):
        self._action_group.set_sensitive(self._window.get_active_document() != None)

    def _scrub(self, string):
        newstr1 = re.sub('^\s*', '', string)
        newstr2 = re.sub('\s*$', '', newstr1)
        cleanlist = re.split('[\s,;]+', newstr2)
        return cleanlist

    def _get_text_selection(self):
        doc = self._window.get_active_document()

        # Get selected text, if any, and get the start and end of it
        if doc.get_has_selection():
            self._start_iter, self._end_iter = doc.get_selection_bounds()
            selected_text = doc.get_text(self._start_iter, self._end_iter)
        else:
            selected_text = ''

        return selected_text

    def _replace_text_selection(self, text):
        doc = self._window.get_active_document()

        doc.begin_user_action()

        # Delete selected text
        doc.delete(self._start_iter, self._end_iter)

        # Mark start of new selection
        start_mark = doc.create_mark(
            mark_name=None,
            where=self._start_iter,
            left_gravity=True)

        # Insert the new text
        doc.insert(self._start_iter, text)

        # Move the selection bound to the new text
        new_start_iter = doc.get_iter_at_mark(start_mark)
        doc.move_mark_by_name("selection_bound", new_start_iter)

        doc.end_user_action()

    def _enclose_text(self, opening_symbol, closing_symbol):
        doc = self._window.get_active_document()
        if not doc:
            return

        selected_text = self._get_text_selection()
        if len(selected_text):
            self._replace_text_selection("%s%s%s" %
                (opening_symbol, selected_text, closing_symbol))

    # Menu activate handlers
    def on_configure_activate(self, action):
        self._plugin.create_configure_dialog()

    def on_encl_braces_activate(self, action):
        self._enclose_text('{', '}')

    def on_encl_brackets_activate(self, action):
        self._enclose_text('[', ']')

    def on_encl_quotes_activate(self, action):
        self._enclose_text('"', '"')

    def on_encl_custom_activate(self, action):
        self._enclose_text(self.options[6], self.options[7])

    def on_make_array_activate(self, action):
        doc = self._window.get_active_document()
        if not doc:
            return

        selected_text = self._get_text_selection()
        if selected_text:
            encl_type = int(self.options[8])
            text_length = len(selected_text)
            char_count = 1
            new_string = "%c " % self.encl_char[encl_type][0]
            for charset in selected_text:
                if char_count < text_length:
                    new_string += ("'%c', " % charset)
                else:
                    new_string += ("'%c'" % charset)
                char_count += 1

            new_string += " %c" % self.encl_char[encl_type][1]
            self._replace_text_selection(new_string)

    def on_make_word_array_activate(self, action):
        doc = self._window.get_active_document()
        if not doc:
            return

        selected_text = self._get_text_selection()
        if selected_text:
            encl_type = int(self.options[9])
            words = self._scrub(selected_text)
            word_count = len(words) - 1
            new_string = "%c " % self.encl_char[encl_type][0]
            for index, word in enumerate(words):
                if index < word_count:
                    new_string += ("'%s', " % word)
                else:
                    new_string += ("'%s'" % word)

            new_string += " %c" % self.encl_char[encl_type][1]
            self._replace_text_selection(new_string)


class StringModPlugin(gedit.Plugin):
    """
    The main plugin class object

    """

    def __init__(self):
        gedit.Plugin.__init__(self)
        self._window = None
        self._instances = {}
        self.plugin_path = None
        self.config_ui = None

    def activate(self, window):
        self._window = window
        self.plugin_path = os.path.dirname(os.path.realpath(__file__))
        self._instances[window] = StringModWindowHelper(self, window)

    def deactivate(self, window):
        self._instances[window].deactivate()
        del self._instances[window]

    def is_configurable(self):
        return True

    def create_configure_dialog(self):
        if not self.config_ui:
            self.config_ui = StringModConfigHelper(self, self._window)
        return self.config_ui.dialog

    def update_ui(self, window):
        self._instances[window].update_ui()

