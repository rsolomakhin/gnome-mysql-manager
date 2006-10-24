##############################################################################
#
# gnome-mysql-manager - Simple tool for managing MySQL database.
# Copyright (C) 2006  Rouslan Solomakhin
#
#   Makefile.am: Input for automake.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
#
# $Id: Makefile.am 17 2006-10-23 17:17:01Z Rouslan.Solomakhin $
#
##############################################################################

edit_py = sed \
	-e 's,@gladedir\@,$(gladedir),g' \
	-e 's,@pixmapsdir\@,$(pixmapsdir),g'

edit_sh = sed \
	-e 's,@scriptfile\@,$(scriptfile),g'

edit_glade = sed \
	-e 's,@icon\@,$(iconfile),g'


# Process the source directory

# Python files
pythondir = $(datadir)/gnome-mysql-manager/python
python_DATA = mysql-manager.py mysqlmanagerconfig.py
scriptfile = $(pythondir)/mysql-manager.py

python_files = mysqlmanagerconfig.py
python_in_files = $(python_files).in

$(python_files): Makefile $(python_in_files)
	rm -f $(python_files)
	$(edit_py) $(python_in_files) >$(python_files)

# Shell script files
bin_SCRIPTS = gnome-mysql-manager

shell_files = gnome-mysql-manager
shell_in_files = $(shell_files).in

$(shell_files): Makefile $(shell_in_files)
	rm -f $(shell_files)
	$(edit_sh) $(shell_in_files) >$(shell_files)

# Glade configuration files
gladedir = $(datadir)/gnome-mysql-manager/glade
glade_DATA = mysql-manager.glade

glade_files = mysql-manager.glade
glade_in_files = $(glade_files).in

iconfile = $(datadir)/pixmaps/gnome-mysql-manager/tool.png

$(glade_files): Makefile $(srcdir)/$(glade_in_files)
	rm -f $(srcdir)/$(glade_files)
	$(edit_glade) $(srcdir)/$(glade_in_files) >$(srcdir)/$(glade_files)


all: $(python_files) $(shell_files) $(glade_files)

CLEANFILES = $(python_files) $(shell_files) $(glade_files)
MAINTAINERCLEANFILES = $(CLEANFILES) Makefile.in

EXTRA_DIST = \
	$(bin_SCRIPTS) \
	$(glade_DATA) \
	$(python_DATA)
