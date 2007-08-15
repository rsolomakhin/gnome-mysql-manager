#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import gconf
import gobject
import socket
import MySQLdb

class MysqlManagerGui:
	"GNOME MySQL Manager"

	# colors
	ui_error_color   = gtk.gdk.color_parse("#FCE94F")
	conn_error_color = gtk.gdk.color_parse("#F57900")
	no_error_color   = gtk.gdk.color_parse("#FFFFFF")
	
	# gconf
	gconf_path_namespace = "/apps/gnome-mysql-manager"
	gconf_host           = "/apps/gnome-mysql-manager/host"
	gconf_port           = "/apps/gnome-mysql-manager/port"
	gconf_user           = "/apps/gnome-mysql-manager/user"

	def __init__(self):
		"Initialize"
		
		gobject.threads_init()
		
		# ui
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_title("GNOME MySQL Manager")
		window.connect("delete_event", self.delete_event)
		window.connect("destroy", self.destroy)
		self.status = gtk.Label()
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_LEFT)
		self.notebook.append_page(self.build_login_widget(), gtk.Label("Login"))
		box = gtk.VBox()
		box.add(self.notebook)
		box.add(self.status)
		window.add(box)

		# gconf
		self.gconf_client = gconf.client_get_default()
		self.gconf_client.add_dir(self.gconf_path_namespace, gconf.CLIENT_PRELOAD_NONE)
		self.gconf_client.notify_add(self.gconf_path_namespace, self.gconf_key_changed)
		self.gconf_client.notify(self.gconf_host)
		self.gconf_client.notify(self.gconf_port)
		self.gconf_client.notify(self.gconf_user)

		window.show_all()

	def gconf_key_changed(self, client, connection_id, entry, user_data=None):
		"Update user interface using gconf settings"

		key_name = entry.get_key()
		
		# host
		if key_name == self.gconf_host:
			host = self.gconf_client.get_string(self.gconf_host)
			if host is not None and host != self.hostEntry.get_text():
				self.hostEntry.set_text(host)
				
		# user
		elif key_name == self.gconf_user:
			user = self.gconf_client.get_string(self.gconf_user)
			if user is not None and user != self.userEntry.get_text():
				self.userEntry.set_text(user)
				
		# port
		if key_name == self.gconf_port:
			port = self.gconf_client.get_int(self.gconf_port)
			if port is not None and port != self.portAdjst.get_value():
				self.portAdjst.set_value(port)

	def delete_event(self, widget, event):
		return False
		
	def destroy(self, widget):
		"Save settings and quit"
	
		# gconf
		self.gconf_client.set_int(self.gconf_port, int(self.portAdjst.get_value()))
		self.gconf_client.set_string(self.gconf_host, self.hostEntry.get_text())
		self.gconf_client.set_string(self.gconf_user, self.userEntry.get_text())
	
		# quit
		gtk.main_quit()

	def main(self):
		gtk.main()

	def build_login_widget(self):
		self.login_widget = gtk.VBox()
		
		self.login_data_box = gtk.VBox()

		self.hostEntry = gtk.Entry()
		self.portAdjst = gtk.Adjustment(value=3306, lower=1, upper=64000, step_incr=1)
		self.portSpinr = gtk.SpinButton(self.portAdjst)
		self.userEntry = gtk.Entry()
		self.passEntry = gtk.Entry()

		self.hostEntry.set_text("localhost")
		self.userEntry.set_text("root")
		
		self.hostEntry.connect("changed", self.update_login_widget)
		self.portSpinr.connect("changed", self.update_login_widget)
		self.userEntry.connect("changed", self.update_login_widget)
		self.passEntry.connect("changed", self.update_login_widget)

		box = gtk.HBox()
		box.add(gtk.Label("Host:"))
		box.add(self.hostEntry)
		self.login_data_box.add(box)

		box = gtk.HBox()
		box.add(gtk.Label("Port:"))
		box.add(self.portSpinr)
		self.login_data_box.add(box)

		box = gtk.HBox()
		box.add(gtk.Label("User:"))
		box.add(self.userEntry)
		self.login_data_box.add(box)

		box = gtk.HBox()
		box.add(gtk.Label("Password:"))
		box.add(self.passEntry)
		self.login_data_box.add(box)

		self.login_button = gtk.Button("Login")
		self.login_button.connect("clicked", self.on_login_button_clicked)
		buttons = gtk.HButtonBox()
		buttons.add(self.login_button)
		
		self.login_widget.add(self.login_data_box)
		self.login_widget.add(buttons)
		
		return self.login_widget
	

	def on_login_button_clicked(self, widget, data=None):
		host = self.hostEntry.get_text()
		port = int(self.portAdjst.get_value())
		self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.connection.settimeout(1)
		connection_error = None
		try:
			self.connection.connect((host, port))
		except socket.error, error:
			connection_error = error
		finally:
			self.connection.close()
		if connection_error is None:
			self.login()
		else:
			try:
				error_message = connection_error[len(connection_error)-1]
			except TypeError: # TypeError="Object 'timeout' has no len()"
				error_message = "Connection timed out"
			self.status.set_text(error_message+".")
			self.portSpinr.modify_base(gtk.STATE_NORMAL, self.conn_error_color)
			self.hostEntry.modify_base(gtk.STATE_NORMAL, self.conn_error_color)

	def login(self):
		"Login to the MySQL server and display all databases"

		databases = gtk.TreeStore(str, str)

		host = self.hostEntry.get_text()
		port = int(self.portAdjst.get_value())
		user = self.userEntry.get_text()
		pswd = self.passEntry.get_text()
		title = user+"@"+host+":"+str(port)
		
		try:
			server = MySQLdb.connect(host=host, port=port, user=user, passwd=pswd)
		except MySQLdb.MySQLError, error:
			self.status.set_text(error[1])
			self.userEntry.modify_base(gtk.STATE_NORMAL, self.conn_error_color)
			self.passEntry.modify_base(gtk.STATE_NORMAL, self.conn_error_color)
			return

		cursor = server.cursor()

		# database are keys
		db_dict = {}
		cursor.execute("show databases")
		row = cursor.fetchone()
		while row is not None:
			db = row[0]
			if db != "mysql" and db != "information_schema":
				db_dict[db] = []
			row = cursor.fetchone()

		# try to open mysql database.
		# if this succeeds, manage user permissions.
		# if this fails, view tables.
		super_user = True
		try:
			cursor.execute("use mysql")
		except MySQLdb.MySQLError:
			super_user = False

		if super_user:
			# lists of (host, user) tuples are values
			for db, users in db_dict.iteritems():
				cursor.execute("select host,user from db where db=%s", (db,));
				row = cursor.fetchone()
				while row is not None:
					host = row[0]
					user = row[1]
					users.append((host, user))
					row = cursor.fetchone()
		else:
			# lists of tables are values
			for db, tables in db_dict.iteritems():
				cursor.execute("use "+db)
				cursor.execute("show tables")
				row = cursor.fetchone()
				while row is not None:
					table = row[0]
					tables.append(table)
					row = cursor.fetchone()
		
		cursor.close()

		# Populate the treemodel.
		if super_user:
	 		for db, users in db_dict.iteritems():
				parent_row = databases.append(None, [db, None])
				for host, user in users:
					databases.append(parent_row, [host, user])
		else:
			for db, tables in db_dict.iteritems():
				parent_row = databases.append(None, [db, None])
				for table in tables:
					databases.append(parent_row, [table, None])

		view = gtk.TreeView(databases)
		
		# first column is databases
		column1 = gtk.TreeViewColumn()
		view.append_column(column1)
		renderer1 = gtk.CellRendererText()
		column1.pack_start(renderer1, True)
		column1.add_attribute(renderer1, "text", 0)
		column1.set_sort_column_id(0)

		if super_user:
			# second column is users
			column2 = gtk.TreeViewColumn()
			view.append_column(column2)
			renderer2 = gtk.CellRendererText()
			column2.pack_start(renderer2, True)
			column2.add_attribute(renderer2, "text", 1)
			column2.set_sort_column_id(0)
		
		view.set_search_column(0)

		scrolled_window = gtk.ScrolledWindow()
		scrolled_window.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
		scrolled_window.add(view)
		self.notebook.prepend_page(scrolled_window, gtk.Label(title))
		self.notebook.show_all()
		self.notebook.set_current_page(0)
		return

	def update_login_widget(self, widget, event=None):
		"Color widgets depending on user input"

		errors = ""
		host = self.hostEntry.get_text()

		self.portSpinr.modify_base(gtk.STATE_NORMAL, self.no_error_color)
		self.passEntry.modify_base(gtk.STATE_NORMAL, self.no_error_color)

		# Color the host entry if it is empty.
		if host == "":
			self.hostEntry.modify_base(gtk.STATE_NORMAL, self.ui_error_color)
			errors += "Hostname missing. "
		else:
			self.hostEntry.modify_base(gtk.STATE_NORMAL, self.no_error_color)

		# Color the user entry if it is empty.
		if self.userEntry.get_text() == "":
			self.userEntry.modify_base(gtk.STATE_NORMAL, self.ui_error_color)
			errors += "Username missing. "
		else:
			self.userEntry.modify_base(gtk.STATE_NORMAL, self.no_error_color)


		self.status.set_text(errors)
		self.login_button.set_sensitive(len(errors) == 0)
		
if __name__ == "__main__":
	mysql_manager_gui = MysqlManagerGui()
	mysql_manager_gui.main()
