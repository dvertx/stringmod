# -*- coding: utf-8 -*-
#
#  Configuration module of String Modifiers plugin for gedit
#
#  Copyright (C) 2010, Hertatijanto Hartono <dvertx@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
2010-12-01  for String Modifiers plugin version 1.0

This module provides dialog box for configuring String Modifiers plugin.

"""

import os
import re
import sys
import gtk
from gettext import gettext as _

class StringModConfigHelper:

    """
    Configuration file:
    -------------------
    |    Accelerators = [ 'AccelBraces', 'AccelBrackets', 'AccelQuotes',
    |                     'AccelCustom', 'AccelStr2Array', 'AccelStr2WArray' ]
    |
    |    Custom enclosures = [ 'CustomStart', 'CustomEnd' ]
    |
    |    String to Arrary enclodsure choice = [ 'RadioCharArray', 'RadioWordArray' ]
    -------------------

    The configuration then parsed into options list

    """

    options = [ '', '', '', '', '', '', '"', '"', 0, 0 ]
    
    encl_char = (('{', '}'), ('[', ']'), ('(', ')'))
    
    widget_names = [ 'AccelBraces', 'AccelBrackets', 'AccelQuotes', 'AccelCustom',
                     'AccelStr2Array', 'AccelStr2WArray', 'CustomStart', 'CustomEnd' ]
    
    radio_char_names = [ 'RadioCharArray1', 'RadioCharArray2', 'RadioCharArray3' ]
    
    radio_word_names = [ 'RadioWordArray1', 'RadioWordArray2', 'RadioWordArray3' ]
    
    widget_objects = []
    widget_values = []
    radio_char_objects = []
    radio_word_objects = []

    action_path = '<Actions>/StringModPluginActions/'
    action_list = [ 'Braces', 'Brackets', 'Quotes', 'Custom', 
                    'Str2CharArray', 'Str2WordArray' ]


    def __init__(self, plugin, window):
        self._window = window
        self._plugin = plugin

        self.RadioCharArray = 0
        self.RadioWordArray = 0

        self.Accelerator = ''
        self.OldAccel = ''
        self.accel_index = None

        self._parse_config_file()

        glade_file = os.path.join(self._plugin.plugin_path, 'strmodconf.glade')
        self.builder = gtk.Builder()
        self.builder.add_from_file(glade_file)
        self.dialog = self.builder.get_object("maindialog")
        self._get_dialog_widgets_objects()
        self._set_dialog_widgets_from_options_values()
        self.builder.connect_signals(self)
        self.dialog.set_transient_for(self._window)
        self.dialog.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.dialog.show()

    def _parse_config_file(self):
        self.config_file_name = os.path.join(self._plugin.plugin_path, 'stringmod.cfg')
        if os.path.exists(self.config_file_name):
            # Set global options from config file entries
            index = 0
            for line in open(self.config_file_name):
                params = self._split(line)
                if index < len(self.widget_names):
                    self.options[index] = params[1]
                else:
                    self.options[index] = int(params[1])
                index += 1
        else:
            self._set_config_file()

    def _set_config_file(self):
        self.conf_file = open(self.config_file_name, 'wb')
        for index, name in enumerate(self.widget_names):
            self.conf_file.write("%s=%s\n" % (name, self.options[index]))

        index += 1
        self.conf_file.write("RadioCharArray=%s\n" % str(self.options[index]))
        index += 1
        self.conf_file.write("RadioWordArray=%s\n" % str(self.options[index]))
        self.conf_file.close()

    def _split(self, string):
        newstr = re.sub('\s$', '', string)
        cleanlist = re.split('=', newstr)
        return cleanlist

    def _get_dialog_widgets_objects(self):
        for widget in self.widget_names:
            widget_object = self.builder.get_object(widget)
            self.widget_objects.append(widget_object)

        for radio_char in self.radio_char_names:
            radio_char_object = self.builder.get_object(radio_char)
            self.radio_char_objects.append(radio_char_object)

        for radio_word in self.radio_word_names:
            radio_word_object = self.builder.get_object(radio_word)
            self.radio_word_objects.append(radio_word_object)

    def _get_dialog_widgets_values(self):
        for widget_object in self.widget_objects:
            widget_value = widget_object.get_text()
            self.widget_values.append(widget_value)

    def _set_dialog_widgets_from_options_values(self):
        for index, widget_object in enumerate(self.widget_objects):
            widget_object.set_text(self.options[index])

        index += 1
        self.radio_char_objects[self.options[index]].set_active(True)
        self.RadioCharArray = self.options[index]
        index += 1
        self.radio_word_objects[self.options[index]].set_active(True)
        self.RadioWordArray = self.options[index]

    def _set_options_from_widgets_values(self):
        for index, value in enumerate(self.widget_values):
            self.options[index] = value

        index += 1
        self.options[index] = self.RadioCharArray
        index += 1
        self.options[index] = self.RadioWordArray

    def on_radio_char_toggled(self, widget, data=None):
        for index, radio_object in enumerate(self.radio_char_objects):
            if widget == radio_object:
                self.RadioCharArray = index

    def on_radio_word_toggled(self, widget, data=None):
        for index, radio_object in enumerate(self.radio_word_objects):
            if widget == radio_object:
                self.RadioWordArray = index

    def on_in_focus_event(self, widget, data=None):
        for index, accelerator in enumerate(self.widget_objects):
            if widget == accelerator:
                self.accel_index = index
                self.OldAccel = widget.get_text()
                widget.set_text('Press new accel keys')
                #### TODO: Tooltips() ######################
                # "Press key combination that you would like
                #  to use as shortcut for this action. Or
                #  press Del key to remove current shortcut."

    def on_focus_out_event(self, widget, data=None):
        gtk.gdk.keyboard_ungrab()
        if not self.Accelerator:
            widget.set_text(self.OldAccel)
        self.Accelerator = ''
        self.accel_index = None

    def _is_valid_accel(self, keyval, mod):
        accel_path = self.action_path + self.action_list[self.accel_index]
        old_accel = gtk.accel_map_lookup_entry(accel_path)
        if not gtk.accel_map_change_entry(accel_path, keyval, mod, False):
            msgdlg = gtk.MessageDialog(self.dialog,
                                       gtk.DIALOG_MODAL,
                                       gtk.MESSAGE_ERROR,
                                       gtk.BUTTONS_OK,
                                       _('Shortcut %s is already in use') % gtk.accelerator_name(keyval, mod))
            msgdlg.run()
            msgdlg.destroy()
            return False
        else:
            gtk.accel_map_change_entry(accel_path, old_accel[0], old_accel[1], True)
            return True

    def on_key_press_event(self, widget, event):
        mask = event.state & gtk.accelerator_get_default_mod_mask()

        if event.keyval == gtk.keysyms.Escape:
            widget.set_text('Press new accel keys')
            return True
        elif event.keyval in (gtk.keysyms.Delete, gtk.keysyms.BackSpace):
            self.OldAccel = ''
            self.Accelerator = ''
            widget.set_text(self.Accelerator)
            return True
        elif event.keyval in range(gtk.keysyms.F1, gtk.keysyms.F12 + 1):
            if self._is_valid_accel(event.keyval, mask):
                self.Accelerator = gtk.accelerator_name(event.keyval, mask)
                widget.set_text(self.Accelerator)
                return True
        elif gtk.gdk.keyval_to_unicode(event.keyval):
            if mask:
                if self._is_valid_accel(event.keyval, mask):
                    self.Accelerator = gtk.accelerator_name(event.keyval, mask)
                    widget.set_text(self.Accelerator)
                    return True
        else:
            return False

    def on_ok_click(self, event):
        self._get_dialog_widgets_values()
        self._set_options_from_widgets_values()

        # Reconfigure accel keys on menu
        for index, action in enumerate(self.action_list):
            accel_value = gtk.accelerator_parse(self.options[index])
            accel_path = self.action_path + action
            gtk.accel_map_change_entry(accel_path, accel_value[0], accel_value[1], False)

        self._set_config_file()
        self.dialog.destroy()

    def on_cancel_click(self, event):
        self.dialog.destroy()

    def deactivate(self, event=None):
        del self.widget_objects[:]
        del self.widget_values[:]
        del self.radio_char_objects[:]
        del self.radio_word_objects[:]

        self._plugin.config_ui = None
        self._window = None
        self._plugin = None

