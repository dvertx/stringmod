# -*- coding: utf-8 -*-
#  String Modifiers plugin for gedit
#
#  Copyright (C) 2010-2011  Hertatijanto Hartono
#
#  This program is free software: you can redistribute it and/or modify
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
String Modifiers plugin package
2010-12-01  Version 1.0

Description:
This plugin tries to provide programmers with the ability to replace selected
text with some predetermined actions, such as enclosing the selected text with
brackets, curly braces or quotes, or converting them into an array of characters
or words, while using gedit as their development editor.

Files:
stringmodifier.gedit-plugin    -- Plugin.
stringmodifier/                -- Package directory
    __init__.py                -- Package module loaded by Gedit.
    stringmod.py               -- Plugin and plugin helper classes.
    strmodconf.py              -- Configuration window class.
    strmodconf.glade           -- Configuration window layout from Glade.

"""
from stringmod import StringModPlugin

