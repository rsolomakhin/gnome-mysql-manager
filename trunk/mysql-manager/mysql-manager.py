##############################################################################
#
# gnome-mysql-manager - Simple tool for managing MySQL database.
# Copyright (C) 2006  Rouslan Solomakhin
#
#   mysql-manager.py: MySQL database manager GUI.
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


import os
import gtk.glade
import gnome.ui
import gobject
import gconf
import MySQLdb
from MySQLdb import *
import mysqlmanagerconfig


##############################################################################
#
#                   GUI for managing MySQL databases.
#
##############################################################################
class MysqlManager:

	
	######################################################################
	# __init__
	# input: none
	# output: none
	# reads interface definition from glade file, creates lists to
	# contain data in columns.
	#
	def __init__(self):
		gnome.init('mysql-manager','0.1')
		self.xml = gtk.glade.XML(os.path.join(
			mysqlmanagerconfig.GLADEDIR,
			'mysql-manager.glade'))
		self.xml.signal_autoconnect(self)

		renderer = gtk.CellRendererText()
		
		self.db_model = gtk.ListStore(gobject.TYPE_STRING)
		self.xml.get_widget('db_treeview').set_model(self.db_model)
		self.xml.get_widget('db_treeview').append_column(
			gtk.TreeViewColumn('Database', renderer, text=0))

		self.perm_model = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING)
		self.xml.get_widget('perm_treeview').set_model(self.perm_model)
		self.xml.get_widget('perm_treeview').append_column(
			gtk.TreeViewColumn('Host', renderer, text=0))
		self.xml.get_widget('perm_treeview').append_column(
			gtk.TreeViewColumn('Database', renderer, text=1))
		self.xml.get_widget('perm_treeview').append_column(
			gtk.TreeViewColumn('User', renderer, text=2))

		self.user_model = gtk.ListStore(
			gobject.TYPE_STRING,
			gobject.TYPE_STRING,
			gobject.TYPE_STRING)
		self.xml.get_widget('user_treeview').set_model(self.user_model)
		self.xml.get_widget('user_treeview').append_column(
			gtk.TreeViewColumn('Host', renderer, text=0))
		self.xml.get_widget('user_treeview').append_column(
			gtk.TreeViewColumn('User', renderer, text=1))
		self.xml.get_widget('user_treeview').append_column(
			gtk.TreeViewColumn('Password', renderer, text=2))


	######################################################################
	# start_gui
	# input: none
	# output: none
	# shows gui.
	#
	def start_gui(self):
		gtk.main()


	######################################################################
	# on_delete
	# input: widget and signal. signal can be omitted.
	# output: always false (release resources for the gui).
	# callback for closing main window.
	#
	def on_delete(self,widget,signal=None):
		gtk.main_quit()
		return False


	######################################################################
	# on_about
	# input: widget.
	# output: none
	# callback for selecting 'about' in a menu.
	#
	def on_about(self,widget):
		self.xml.get_widget('about_dialog').show()


	######################################################################
	# on_about_delete
	# input: widget and signal. the latter can be omitted.
	# output: always true (do not destroy the dialog).
	# callback for closing 'about' dialog.
	#
	def on_about_delete(self,widget,signal=None):
		self.xml.get_widget('about_dialog').hide()
		return True


	######################################################################
	# on_host_entry_changed
	# input: widget.
	# output: none.
	# callback for text changes in host entry. this is the entry
	# that allows to specify hostname of the mysql server to which
	# we are to connect.
	#
	def on_host_entry_changed(self,widget):
		is_localhost = (widget.get_text() == 'localhost')
		self.xml.get_widget('port_spinbutton').set_sensitive(
			not is_localhost)
		if is_localhost:
			self.xml.get_widget('port_spinbutton').set_value(3306)


	######################################################################
	# on_switch_server
	# input: widget.
	# output: none.
	# callback for selecting 'switch server' in menu or clicking
	# this button on toolbar.
	#
	def on_switch_server(self,widget):
		self.xml.get_widget('main_app').hide()
		self.xml.get_widget('server_dialog').show()
		self.xml.get_widget('password_entry').set_text('')


	######################################################################
	# on_change_password
	# input: widget.
	# output: none.
	# callback for selecting the menu item 'change password'.
	#
	def on_change_password(self,widget):
		self.xml.get_widget('change_password_entry1').set_text('')
		self.xml.get_widget('change_password_entry2').set_text('')
		self.on_change_password_entry_changed()
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('password_dialog').show()


	######################################################################
	# on_change_password_entry_changed
	# input: widget, can be omitted.
	# output: none.
	# callback for change in password entries. these are the
	# entries in 'password change' dialog.
	#
	def on_change_password_entry_changed(self,widget=None):
		e1 = self.xml.get_widget('change_password_entry1').get_text()
		e2 = self.xml.get_widget('change_password_entry2').get_text()
		same = (e1 == e2) and (e1 != '')
		self.xml.get_widget('change_password_okbutton').set_sensitive(
			same)


	######################################################################
	# on_change_password_cancel
	# input: widget and signal. the latter can be omitted.
	# output: always true (do not destroy the dialog).
	# callback for pressing button 'cancel' in the 'password
	# change' dialog, or closing the dialog.
	#
	def on_change_password_cancel(self,widget,signal=None):
		self.xml.get_widget('main_app').set_sensitive(True)
		self.xml.get_widget('password_dialog').hide()
		return True


	######################################################################
	# on_change_password_okbutton
	# input: widget.
	# output: none.
	# callback for pressing 'ok' button in dialog 'password change'.
	#
	def on_change_password_okbutton(self,widget):
		p = self.xml.get_widget('change_password_entry1').get_text()
		try:
			c = self.db.cursor()
			c.execute('update mysql.user set password=PASSWORD("'
					  +p+'") where user="'+self.user+'"')
			c = self.db.cursor()
			c.execute('flush privileges')
		except Error, detail:
			self.show_error('Change Password',detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('main_app').set_sensitive(True)
			self.xml.get_widget('password_dialog').hide()


	######################################################################
	# on_add_user
	# input: widget.
	# output: none.
	# callback for clicking 'add user' button.
	#
	def on_add_user(self,widget):
		print 'adding user...'


	######################################################################
	# on_edit_user
	# input: widget, iterator (can be omitted), and path (also can
	#        be omitted).
	# callback for pressing 'edit user' button.
	#
	def on_edit_user(self,widget,iter=None,path=None):
		print 'editing user...'


	######################################################################
	# on_delete_user
	# input: widget.
	# output: none.
	# callback for pressing 'delete user' button.
	#
	def on_delete_user(self,widget):
		print 'deleting user...'


	######################################################################
	# on_add_perm
	# input: widget.
	# output: none.
	# callback for pressing 'add permission' button.
	#
	def on_add_perm(self,widget):
		print 'adding permission...'


	######################################################################
	# on_edit_perm
	# input: widget, iterator (can be omitted), and path (can also
	#        be omitted).
	# output: none.
	# callback for pressing 'edit permission' button.
	#
	def on_edit_perm(self,widget,iter=None,path=None):
		print 'editing permission...'


	######################################################################
	# on_delete_perm
	# input: widget.
	# output: none.
	# callback for pressing 'delete permission' button.
	#
	def on_delete_perm(self,widget):
		print 'deleting permission...'


	######################################################################
	# on_quick_add
	# input: widget.
	# output: none.
	# callback for pressing 'quick add' button. this is the button
	# that allows to add add a new database with new user in one
	# swing.
	#
	def on_quick_add(self,widget):
		self.xml.get_widget('quick_add_host_entry').set_text(
			'localhost')
		self.xml.get_widget('quick_add_db_entry').set_text('')
		self.xml.get_widget('quick_add_user_entry').set_text('')
		self.xml.get_widget('quick_add_password_entry').set_text('')
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('quick_add_dialog').show()
		self.on_quick_add_entry_changed()


	######################################################################
	# on_quick_add_entry_changed
	# input: widget. can be omitted.
	# output: none.
	# callback for changes in text entry of 'quick add' dialog. 
	#
	def on_quick_add_entry_changed(self,widget=None):
		db = self.xml.get_widget('quick_add_db_entry').get_text()
		user = self.xml.get_widget('quick_add_user_entry').get_text()
		ok = (db != '') and (user != '')
		self.xml.get_widget('quick_add_addbutton').set_sensitive(ok)


	######################################################################
	# on_quick_add_cancel
	# input: widget and signal. the latter can be omitted.
	# output: always true (do not release resources for
	#         the dialog).
	# callback for pressing 'cancel' in the 'quick add' dialog, or
	# closing the dialog.
	#
	def on_quick_add_cancel(self,widget,signal=None):
		self.xml.get_widget('quick_add_dialog').hide()
		self.xml.get_widget('main_app').set_sensitive(True)
		return True


	######################################################################
	# on_quick_add_button
	# input: widget.
	# output: none.
	# callback for clicking button 'add' in 'quick add' dialog.
	#
	def on_quick_add_addbutton(self,widget):
		host = self.xml.get_widget('quick_add_host_entry').get_text()
		db = self.xml.get_widget('quick_add_db_entry').get_text()
		user = self.xml.get_widget('quick_add_user_entry').get_text()
		passwd = self.xml.get_widget(
			'quick_add_password_entry').get_text()
		try:
			c = self.db.cursor()
			c.execute('create database '+db)
			c = self.db.cursor()
			c.execute('grant all privileges on '
				  +db+'.* to "'+user+'"@"'+host
				  +'" identified by "'+passwd+'"')
		except Error, detail:
			self.show_error('Add',detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('quick_add_dialog').hide()
			self.xml.get_widget('main_app').set_sensitive(True)


	######################################################################
	# on_add_db
	# input: widget.
	# output: none.
	# callback for clicking button 'add database'.
	#
	def on_add_db(self,widget):
		self.xml.get_widget('add_db_db_entry').set_text('')
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('add_db_dialog').show()
		self.on_add_db_entry_changed(None)


	######################################################################
	# on_cancel_add_db
	# input: widget and signal. the latter can be omitted.
	# output: always true (do not realease resources for
	#         the dialog).
	# callback for pressing 'cancel' button in 'add database'
	# dialog, or closing the dialog.
	#
	def on_cancel_add_db(self,widget,signal=None):
		self.xml.get_widget('add_db_dialog').hide()
		self.xml.get_widget('main_app').set_sensitive(True)
		return True


	######################################################################
	# on_add_db_okbutton
	# input: widget.
	# output: none.
	# callback for clicking button 'ok' in 'add database' dialog.
	#
	def on_add_db_okbutton(self,widget):
		db = self.xml.get_widget('add_db_db_entry').get_text()
		try:
			c = self.db.cursor()
			c.execute('create database '+db)
		except Error, detail:
			self.show_error('Add Database',detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('add_db_dialog').hide()
			self.xml.get_widget('main_app').set_sensitive(True)


	######################################################################
	# on_error_delete
	# input: widget and signal. latter can be omitted.
	# output: always true (do not destroy the dialog).
	# callback for closing the error dialog.
	#
	def on_error_delete(self,widget,signal=None):
		self.xml.get_widget('error_dialog').hide()
		return True


	######################################################################
	# show_error
	# input: a taks that produced the erorr and the error
	#        message.
	# output: none.
	# shows an error dialog with given message.
	#
	def show_error(self,task,message):
		self.xml.get_widget('error_title').set_text(
			'<span size="large"><b>Unable to '+task+'</b></span>')
		self.xml.get_widget('error_label').set_text(message)
		self.xml.get_widget('error_dialog').show()


	######################################################################
	# on_add_db_entry_changed
	# input: widget.
	# output: none.
	# callback for change in text entry of 'add database' dialog. 
	#
	def on_add_db_entry_changed(self,widget):
		self.xml.get_widget('add_db_okbutton').set_sensitive(
			self.xml.get_widget(
			'add_db_db_entry').get_text() != '')


	######################################################################
	# on_delete_db
	# input: widget.
	# output: none.
	# callback for pressing 'delete database' button.
	#
	def on_delete_db(self,widget):
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('delete_db_dialog').show()


	######################################################################
	# on_cancel_delete_db
	# input: widget and signal. the latter can be omitted.
	# output: always true (do not destory the dialog).
	# callback for pressing 'cancel' in 'delete database' dialog,
	# or closing the dialog.
	#
	def on_cancel_delete_db(self,widget,signal=None):
		self.xml.get_widget('delete_db_dialog').hide()
		self.xml.get_widget('main_app').set_sensitive(True)
		return True


	######################################################################
	# on_delete_db_deletebutton
	# input: widget.
	# output: none.
	# callback for pressing 'delete' button in 'delete database'
	# dialog.
	#
	def on_delete_db_deletebutton(self,widget):
		(model, iter) = self.xml.get_widget(
			'db_treeview').get_selection().get_selected()
		db = model.get(iter, 0)
		try:
			c = self.db.cursor()
			c.execute('drop database '+db[0])
		except Error, detail:
			self.show_error('Delete Database',detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('delete_db_dialog').hide()
			self.xml.get_widget('main_app').set_sensitive(True)


	######################################################################
	# populate_models
	# input: widget, can be omitted.
	# output: none.
	# populates lists with data. these are the lists to be
	# displayed to user in gui.
	#
	def populate_models(self,widget=None):
		self.db_model.clear()
		self.perm_model.clear()
		self.user_model.clear()
		try:
			c = self.db.cursor()
			c.execute('show databases')
			for r in c.fetchall():
				self.db_model.append(r)
			c = self.db.cursor()
			c.execute('select host,db,user from mysql.db')
			for r in c.fetchall():
				self.perm_model.append(r)
			c = self.db.cursor()
			c.execute('select host,user,password from mysql.user')
			for r in c.fetchall():
				self.user_model.append(r)
		except Error, detail:
			self.show_error('Use Database',detail[1])
		self.on_select_db_row()
		self.on_select_perm_row()
		self.on_select_user_row()


	######################################################################
	# on_select_db_row
	# input: widget, can be ommited.
	# output: none.
	# callback for selecting a row in the list of databases.
	#
	def on_select_db_row(self,widget=None):
		(model, iter) = self.xml.get_widget(
			'db_treeview').get_selection().get_selected()
		sel = False
		if iter:
			db = model.get(iter, 0)
			sel = ((db[0] != 'mysql') and
			       (db[0] != 'information_schema'))
		self.xml.get_widget('delete_db_button').set_sensitive(sel)
		self.xml.get_widget('delete_db_menu_item').set_sensitive(sel)
	

	######################################################################
	# on_select_user_row
	# input: widget, can be omitted.
	# output: none.
	# callback for selecting a row in the list of users.
	#
	def on_select_user_row(self,widget=None):
		(model, iter) = self.xml.get_widget(
			'user_treeview').get_selection().get_selected()
		sel = False
		if iter:
			user = model.get(iter, 1)
			sel = (user[0] != None)
		self.xml.get_widget('delete_user_button').set_sensitive(sel)
		self.xml.get_widget('delete_user_menu_item').set_sensitive(sel)
		self.xml.get_widget('edit_user_button').set_sensitive(sel)
		self.xml.get_widget('edit_user_menu_item').set_sensitive(sel)


	######################################################################
	# on_select_perm_row
	# input: widget, can be omitted.
	# output: none.
	# callback for selecting a row in the list of permissions.
	#
	def on_select_perm_row(self,widget=None):
		(model, iter) = self.xml.get_widget(
			'perm_treeview').get_selection().get_selected()
		sel = False
		if iter:
			user = model.get(iter, 2)
			sel = (user[0] != None)
		self.xml.get_widget('delete_perm_button').set_sensitive(sel)
		self.xml.get_widget('delete_perm_menu_item').set_sensitive(sel)
		self.xml.get_widget('edit_perm_button').set_sensitive(sel)
		self.xml.get_widget('edit_perm_menu_item').set_sensitive(sel)


	######################################################################
	# on_connect
	# input: widget.
	# output: none.
	# callback for pressing 'connect' button in the 'connect to
	# server' dialog.
	#
	def on_connect(self,widget):
		host_entry = self.xml.get_widget('server_entry').get_text()
		port_spin = self.xml.get_widget(
			'port_spinbutton').get_value_as_int()
		user_entry = self.xml.get_widget('username_entry').get_text()
		passwd_entry = self.xml.get_widget('password_entry').get_text()
		try:
			self.db = MySQLdb.connect(
				host = host_entry,
				port = port_spin,
				user = user_entry,
				passwd = passwd_entry)
		except Error, detail:
			self.show_error('Login',detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('server_dialog').hide()
			self.xml.get_widget('main_app').set_title(
				'MySQL Manager ('+user_entry+'@'+host_entry
				+':'+str(port_spin)+')')
			self.xml.get_widget('main_app').show()
			self.user = user_entry


##############################################################################
# 
#           Load and show GUI if ran from command line.
#
##############################################################################
if __name__ == '__main__':
	app = MysqlManager()
	app.start_gui()


##############################################################################
