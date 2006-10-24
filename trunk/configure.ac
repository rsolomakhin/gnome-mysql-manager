dnl
dnl gnome-mysql-manager - Simple tool for managing MySQL database.
dnl Copyright (C) 2006  Rouslan Solomakhin
dnl
dnl   configure.ac: General directions for configuring this application.
dnl
dnl This program is free software; you can redistribute it and/or modify
dnl it under the terms of the GNU General Public License as published by
dnl the Free Software Foundation; either version 2 of the License, or
dnl (at your option) any later version.
dnl
dnl This program is distributed in the hope that it will be useful,
dnl but WITHOUT ANY WARRANTY; without even the implied warranty of
dnl MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
dnl GNU General Public License for more details.
dnl
dnl You should have received a copy of the GNU General Public License
dnl along with this program; if not, write to the Free Software
dnl Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
dnl USA
dnl
dnl $Id$
dnl

AC_PREREQ(2.59)

AC_INIT([MySQL Manager], [0.1])
AC_CONFIG_SRCDIR(HACKING)
AC_COPYRIGHT([Copyright (C) 2006 Rouslan Solomakhin])

AM_INIT_AUTOMAKE

AC_PATH_PROG(PYTHON, python)

RVL_PYTHON_MODULE(gtk,     yes)
RVL_PYTHON_MODULE(gnome,   yes)
RVL_PYTHON_MODULE(gobject, yes)
RVL_PYTHON_MODULE(gconf,   yes)
RVL_PYTHON_MODULE(MySQLdb, yes)

AC_CONFIG_FILES([
Makefile
mysql-manager/Makefile
pixmaps/Makefile
])

AC_OUTPUT
