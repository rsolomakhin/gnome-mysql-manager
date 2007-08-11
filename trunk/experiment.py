#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import socket
import threading

class MysqlManagerTestConn(threading.Thread):
	def __init__(self, host, port):
		threading.Thread.__init__(self)
		self.host = host
		self.port = port
		self.error = None

	def run(self):
		"""Return None on successful connection.
		   Return (error_num, error_message) on error."""
		connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			connection.connect((self.host, self.port))
		except socket.error, error:
			self.error = error
		connection.close()

class MysqlManagerSocket:
	def __init__(self, plug_id):
		w = gtk.Window(gtk.WINDOW_TOPLEVEL)
		s = gtk.Socket()
		w.add(s)
		s.add_id(plug_id)
		w.connect("delete_event", self.delete_event)
		w.connect("destroy", self.destroy)
		w.show_all()

	def delete_event(self, widget, event):
		return False
		
	def destroy(self, widget):
		gtk.main_quit()

	def main(self):
		gtk.main()

class MysqlManagerPlug:
	def __init__(self):
		self.plug = gtk.Plug(0L)
		self.status = gtk.Label()
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_LEFT)
		self.notebook.append_page(self.build_login_widget(), gtk.Label("Login"))
		box = gtk.VBox()
		box.add(self.notebook)
		box.add(self.status)
		self.plug.add(box)
		self.plug.show_all()

	def get_id(self):
		return self.plug.get_id()

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
		self.userEntry.connect("changed", self.update_login_widget)
		self.portSpinr.connect("changed", self.update_login_widget)

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
		self.login_button.connect("clicked", self.login)
		self.cancel_button = gtk.Button("Cancel")
		self.cancel_button.connect("clicked", self.cancel_login)
		self.cancel_button.set_sensitive(False)
		buttons = gtk.HButtonBox()
		buttons.add(self.cancel_button)
		buttons.add(self.login_button)
		
		self.login_widget.add(self.login_data_box)
		self.login_widget.add(buttons)
		
		return self.login_widget

	def login(self, widget, data=None):
		self.set_connecting_status(True)
		host = self.hostEntry.get_text()
		port = int(self.portAdjst.get_value())
		background = MysqlManagerTestConn(host, port)
		background.start()
		background.join()
		self.set_connecting_status(False)
		if background.error != None:
			num = background.error[0]
			mes = background.error[1]
			self.status.set_text(mes+".")
			orange = gtk.gdk.color_parse("#F57900")
			if num == 111:
				self.portSpinr.modify_base(gtk.STATE_NORMAL, orange)
			elif num == -5 or num == -2 or num == 113:
				self.hostEntry.modify_base(gtk.STATE_NORMAL, orange)
			elif num == 111:
				self.portSpinr.modify_base(gtk.STATE_NORMAL, orange)
				self.hostEntry.modify_base(gtk.STATE_NORMAL, orange)
			else:
				print "Error #", num
				self.portSpinr.modify_base(gtk.STATE_NORMAL, orange)
				self.hostEntry.modify_base(gtk.STATE_NORMAL, orange)
			return
		user = self.userEntry.get_text()
		pswd = self.passEntry.get_text()
		title = user+"@"+host+":"+str(port)
		
		databases = gtk.TreeStore(str)
		databases.append(None, ["hello"])
		databases.append(None, ["good bye"])
		view = gtk.TreeView(databases)
		column = gtk.TreeViewColumn("Database")
		view.append_column(column)
		cell = gtk.CellRendererText()
		column.pack_start(cell, True)
		column.add_attribute(cell, "text", 0)
		view.set_search_column(0)
		column.set_sort_column_id(0)
		
		self.notebook.prepend_page(view, gtk.Label(title))
		self.notebook.show_all()
		self.notebook.set_current_page(0)
		return

	def set_connecting_status(self, is_connecting):
		self.login_data_box.set_sensitive(not is_connecting)
		self.login_button.set_sensitive(not is_connecting)
		self.cancel_button.set_sensitive(is_connecting)
		if is_connecting:
			self.status.set_text("Connecting...")
		else:
			self.status.set_text("")

	def cancel_login(self, widget, data=None):
		self.conn_thread.stop()
		self.test_conn.close()
		self.set_connecting_status(False)		

	def update_login_widget(self, widget, event=None):
		yellow = gtk.gdk.color_parse("#FCE94F")
		white = gtk.gdk.color_parse("#FFFFFF")
		errors = ""
		if self.hostEntry.get_text() == "":
			self.hostEntry.modify_base(gtk.STATE_NORMAL, yellow)
			errors += "Hostname missing. "
		else:
			self.hostEntry.modify_base(gtk.STATE_NORMAL, white)
		if self.userEntry.get_text() == "":
			self.userEntry.modify_base(gtk.STATE_NORMAL, yellow)
			errors += "Username missing. "
		else:
			self.userEntry.modify_base(gtk.STATE_NORMAL, white)
		self.portSpinr.modify_base(gtk.STATE_NORMAL, white)
		self.login_button.set_sensitive(len(errors) == 0)
		self.status.set_text(errors)

if __name__ == "__main__":
	mysql_manager_plug = MysqlManagerPlug()
	mysql_manager_socket = MysqlManagerSocket(mysql_manager_plug.get_id())
	mysql_manager_socket.main()

