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
# $Id$
#
##############################################################################

PYTHON = python

edit_py = sed \
	-e 's,@gladedir\@,$(gladedir),g' \
	-e 's,@pixmapsdir\@,$(pixmapsdir),g'

edit_sh = sed \
	-e 's,@scriptfile\@,$(scriptfile),g'

edit_glade = sed \
	-e 's,@icon\@,$(iconfile),g'

# Required to allow editing with sed.
distcheck-hook:
	find $(distdir) -type d -name src -maxdepth 1 -exec chmod ug+w {} \;

# Process the pixmaps directory

pixmapsdir = $(datadir)/pixmaps/gnome-mysql-manager
pixmaps_DATA = $(srcdir)/pixmaps/tool.png
iconfile = $(pixmapsdir)/tool.png

# Process the source directory

bin_SCRIPTS = $(srcdir)/mysql-manager/gnome-mysql-manager

pythondir = $(datadir)/gnome-mysql-manager/python
python_DATA = $(srcdir)/mysql-manager/mysql-manager.py \
	$(srcdir)/mysql-manager/mysqlmanagerconfig.py
scriptfile = $(pythondir)/mysql-manager.py

shell_files = $(srcdir)/mysql-manager/gnome-mysql-manager
shell_in_files = $(shell_files).in

$(shell_files): Makefile $(srcdir)/$(shell_in_files)
	rm -f $(srcdir)/$(shell_files) $(srcdir)/$(shell_files).tmp
	$(edit_sh) $(srcdir)/$(shell_in_files) >$(srcdir)/$(shell_files).tmp
	mv $(srcdir)/$(shell_files).tmp $(srcdir)/$(shell_files)

glade_files = $(srcdir)/mysql-manager/mysql-manager.glade
glade_in_files = $(glade_files).in

$(glade_files): Makefile $(srcdir)/$(glade_in_files)
	rm -f $(srcdir)/$(glade_files) $(srcdir)/$(glade_files).tmp
	$(edit_glade) $(srcdir)/$(glade_in_files) >$(srcdir)/$(glade_files).tmp
	mv $(srcdir)/$(glade_files).tmp $(srcdir)/$(glade_files)

python_files = $(srcdir)/mysql-manager/mysqlmanagerconfig.py
python_in_files = $(python_files).in
python_PYTHON = $(python_files)

$(python_files): Makefile $(srcdir)/$(python_in_files)
	rm -f $(srcdir)/$(python_files) $(srcdir)/$(python_files).tmp
	$(edit_py) $(srcdir)/$(python_in_files) >$(srcdir)/$(python_files).tmp
	mv $(srcdir)/$(python_files).tmp $(srcdir)/$(python_files)

gladedir = $(datadir)/gnome-mysql-manager/glade
glade_DATA = $(srcdir)/mysql-manager/mysql-manager.glade

dist_scripts = $(srcdir)/mysql-manager/gnome-mysql-manager

all: $(python_files) $(shell_files) $(glade_files)

CLEANFILES = $(python_files) $(shell_files) $(glade_files)

EXTRA_DIST = \
	$(bin_SCRIPTS) \
	$(dist_SCRIPTS) \
	$(glade_DATA) \
	$(python_files) \
	$(pixmaps_DATA)
