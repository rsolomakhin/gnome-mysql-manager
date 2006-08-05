#!/usr/bin/env python
#
# Rouslan Solomakhin
# Created: Jul 30, 2006
#

import gtk.glade
import gnome.ui
import gobject
import gconf
import MySQLdb
from MySQLdb import *

#
# Class for managing MySQL databases.
#
class MysqlManager:
	def __init__(self):
		gnome.init('mysql-manager','0.1')
		self.xml = gtk.glade.XML('mysql-manager.glade')
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
		
	def start_gui(self):
		gtk.main()

	def on_delete(self,widget,signal=None):
		gtk.main_quit()
		return False

	def on_about(self,widget):
		self.xml.get_widget('about_dialog').show()

	def on_about_delete(self,widget,signal=None):
		self.xml.get_widget('about_dialog').hide()
		return True

	def on_switch_server(self,widget):
		self.xml.get_widget('main_app').hide()
		self.xml.get_widget('server_dialog').show()
		self.xml.get_widget('password_entry').set_text('')
		
	def on_change_password(self,widget):
		self.xml.get_widget('change_password_entry1').set_text('')
		self.xml.get_widget('change_password_entry2').set_text('')
		self.on_change_password_entry_changed()
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('password_dialog').show()

	def on_change_password_entry_changed(self,widget=None):
		e1 = self.xml.get_widget('change_password_entry1').get_text()
		e2 = self.xml.get_widget('change_password_entry2').get_text()
		same = (e1 == e2) and (e1 != '')
		self.xml.get_widget('change_password_okbutton').set_sensitive(same)

	def on_change_password_cancel(self,widget,signal=None):
		self.xml.get_widget('main_app').set_sensitive(True)
		self.xml.get_widget('password_dialog').hide()
		return True

	def on_change_password_okbutton(self,widget):
		p = self.xml.get_widget('change_password_entry1').get_text()
		try:
			c = self.db.cursor()
			c.execute('update mysql.user set password=PASSWORD("'
					  +p+'") where user="'+self.user+'"')
			c = self.db.cursor()
			c.execute('flush privileges')
		except Error, detail:
			self.show_error(detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('main_app').set_sensitive(True)
			self.xml.get_widget('password_dialog').hide()

	def on_add_user(self,widget):
		print 'adding user...'

	def on_edit_user(self,widget,iter=None,path=None):
		print 'editing user...'

	def on_delete_user(self,widget):
		print 'deleting user...'

	def on_add_perm(self,widget):
		print 'adding permission...'

	def on_edit_perm(self,widget,iter=None,path=None):
		print 'editing permission...'

	def on_delete_perm(self,widget):
		print 'deleting permission...'

	def on_quick_add(self,widget):
		self.xml.get_widget('quick_add_host_entry').set_text('localhost')
		self.xml.get_widget('quick_add_db_entry').set_text('')
		self.xml.get_widget('quick_add_user_entry').set_text('')
		self.xml.get_widget('quick_add_password_entry').set_text('')
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('quick_add_dialog').show()
		self.on_quick_add_entry_changed()

	def on_quick_add_entry_changed(self,widget=None):
		db = self.xml.get_widget('quick_add_db_entry').get_text()
		user = self.xml.get_widget('quick_add_user_entry').get_text()
		ok = (db != '') and (user != '')
		self.xml.get_widget('quick_add_addbutton').set_sensitive(ok)

	def on_quick_add_cancel(self,widget,signal=None):
		self.xml.get_widget('quick_add_dialog').hide()
		self.xml.get_widget('main_app').set_sensitive(True)
		return True

	def on_quick_add_addbutton(self,widget):
		host = self.xml.get_widget('quick_add_host_entry').get_text()
		db = self.xml.get_widget('quick_add_db_entry').get_text()
		user = self.xml.get_widget('quick_add_user_entry').get_text()
		passwd = self.xml.get_widget('quick_add_password_entry').get_text()
		try:
			c = self.db.cursor()
			c.execute('create database '+db)
			c = self.db.cursor()
			c.execute('grant all privileges on '+db+'.* to "'
					  +user+'"@"'+host+'" identified by "'+passwd+'"')
		except Error, detail:
			self.show_error(detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('quick_add_dialog').hide()
			self.xml.get_widget('main_app').set_sensitive(True)

	def on_add_db(self,widget):
		self.xml.get_widget('add_db_db_entry').set_text('')
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('add_db_dialog').show()
		self.on_add_db_entry_changed(None)

	def on_cancel_add_db(self,widget,signal=None):
		self.xml.get_widget('add_db_dialog').hide()
		self.xml.get_widget('main_app').set_sensitive(True)
		return True

	def on_add_db_okbutton(self,widget):
		db = self.xml.get_widget('add_db_db_entry').get_text()
		try:
			c = self.db.cursor()
			c.execute('create database '+db)
		except Error, detail:
			self.show_error(detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('add_db_dialog').hide()
			self.xml.get_widget('main_app').set_sensitive(True)

	def on_error_delete(self,widget,signal=None):
		self.xml.get_widget('error_dialog').hide()
		return True

	def show_error(self,message):
		self.xml.get_widget('error_label').set_text(message)
		self.xml.get_widget('error_dialog').show()

	def on_add_db_entry_changed(self,widget):
		self.xml.get_widget('add_db_okbutton').set_sensitive(
			self.xml.get_widget('add_db_db_entry').get_text() != '')
	
	def on_delete_db(self,widget):
		self.xml.get_widget('main_app').set_sensitive(False)
		self.xml.get_widget('delete_db_dialog').show()

	def on_cancel_delete_db(self,widget,signal=None):
		self.xml.get_widget('delete_db_dialog').hide()
		self.xml.get_widget('main_app').set_sensitive(True)
		return True

	def on_delete_db_deletebutton(self,widget):
		(model, iter) = self.xml.get_widget(
			'db_treeview').get_selection().get_selected()
		db = model.get(iter, 0)
		try:
			c = self.db.cursor()
			c.execute('drop database '+db[0])
		except Error, detail:
			self.show_error(detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('delete_db_dialog').hide()
			self.xml.get_widget('main_app').set_sensitive(True)

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
			self.show_error(detail[1])
		self.on_select_db_row()
		self.on_select_perm_row()
		self.on_select_user_row()

	def on_select_db_row(self,widget=None):
		(model, iter) = self.xml.get_widget(
			'db_treeview').get_selection().get_selected()
		sel = False
		if iter:
			db = model.get(iter, 0)
			sel = (db[0] != 'mysql') and (db[0] != 'information_schema')
		self.xml.get_widget('delete_db_button').set_sensitive(sel)
		self.xml.get_widget('delete_db_menu_item').set_sensitive(sel)
		
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

	def on_connect(self,widget):
		host_entry = self.xml.get_widget('server_entry').get_text()
		port_spin = self.xml.get_widget('port_spinbutton').get_value_as_int()
		user_entry = self.xml.get_widget('username_entry').get_text()
		passwd_entry = self.xml.get_widget('password_entry').get_text()
		try:
			self.db = MySQLdb.connect(
				host = host_entry,
				# Does not work:
				port = port_spin,
				user = user_entry,
				passwd = passwd_entry)
		except Error, detail:
			self.show_error(detail[1])
		else:
			self.populate_models()
			self.xml.get_widget('server_dialog').hide()
			self.xml.get_widget('main_app').set_title(
				'MySQL Manager ('+user_entry+'@'+host_entry
				+':'+str(port_spin)+')')
			self.xml.get_widget('main_app').show()
			self.user = user_entry

if __name__ == '__main__':
	app = MysqlManager()
	app.start_gui()
