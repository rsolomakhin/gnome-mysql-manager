dnl
dnl gnome-mysql-manager - Simple tool for managing MySQL database.
dnl Copyright (C) 2006  Rouslan Solomakhin
dnl
dnl   acinclude.m4: Macro for checking existence of python
dnl                 modules. Borrowed from application called
dnl                 'revelation'.
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

AC_DEFUN([RVL_PYTHON_MODULE], [
	AC_MSG_CHECKING(python module $1)

	$PYTHON -c "import imp; imp.find_module('$1')" 2>/dev/null

	if test $? -eq 0; then
		AC_MSG_RESULT(yes)
		eval AS_TR_CPP(HAVE_PYMOD_$1)=yes
	else
		AC_MSG_RESULT(no)
		AC_MSG_ERROR(failed to find module $1)
		exit 1
	fi
])

