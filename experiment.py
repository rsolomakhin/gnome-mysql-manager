#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk
import socket
import threading
import gobject

class MysqlManager:
	def __init__(self):
		gobject.threads_init()
		gtk.gdk.threads_init()
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete)
		self.window.connect("destroy", self.destroy)
		self.status = gtk.Label()
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_LEFT)
		self.notebook.append_page(self.build_login_widget(), gtk.Label("Login"))
		box = gtk.VBox()
		box.add(self.notebook)
		box.add(self.status)
		self.window.add(box)
		self.window.show_all()

	def build_login_widget(self):
		self.login_widget = gtk.VBox()
		self.hostEntry = gtk.Entry()
		self.portAdjst = gtk.Adjustment(value=3306, lower=1, upper=64000, step_incr=1)
		self.portSpinr = gtk.SpinButton(self.portAdjst)
		self.userEntry = gtk.Entry()
		self.passEntry = gtk.Entry()

		self.hostEntry.set_text("localhost")
		self.userEntry.set_text("root")
		
		self.hostEntry.connect("key_release_event", self.update_login_widget)
		self.userEntry.connect("key_release_event", self.update_login_widget)
		#self.portSpinr.connect("key_release_event", self.update_login_widget)
		self.portAdjst.connect("value_changed", self.update_login_widget)

		box = gtk.HBox()
		box.add(gtk.Label("Host:"))
		box.add(self.hostEntry)
		self.login_widget.add(box)

		box = gtk.HBox()
		box.add(gtk.Label("Port:"))
		box.add(self.portSpinr)
		self.login_widget.add(box)

		box = gtk.HBox()
		box.add(gtk.Label("User:"))
		box.add(self.userEntry)
		self.login_widget.add(box)

		box = gtk.HBox()
		box.add(gtk.Label("Password:"))
		box.add(self.passEntry)
		self.login_widget.add(box)

		self.login_button = gtk.Button("Login")
		self.login_button.connect("clicked", self.login)
		self.login_widget.add(self.login_button)
			
		return self.login_widget

	def login_thread(self):
		gtk.gdk.threads_enter()
		host = self.hostEntry.get_text()
		port = int(self.portAdjst.get_value())
		user = self.userEntry.get_text()
		pswd = self.passEntry.get_text()
		title = user+"@"+host+":"+str(port)
		# ccheck host and port
		conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			conn.connect((host, port))
		except socket.error, (num, message):
			self.login_widget.set_sensitive(True)
			self.status.set_text(message+".")
			orange = gtk.gdk.color_parse("#F57900")
			if num == 111:
				self.portSpinr.modify_base(gtk.STATE_NORMAL, orange)
			elif num == -5 or num == -2 or num == 113:
				self.hostEntry.modify_base(gtk.STATE_NORMAL, orange)
			else:
				print "Error #", num
				self.portSpinr.modify_base(gtk.STATE_NORMAL, orange)
				self.hostEntry.modify_base(gtk.STATE_NORMAL, orange)
			gtk.gdk.threads_leave()
			return
		conn.close()
		view = gtk.TreeView()
		self.notebook.prepend_page(view, gtk.Label(title))
		view.show_all()
		self.notebook.set_current_page(0)
		self.login_widget.set_sensitive(True)
		self.status.set_text("")
		gtk.gdk.threads_leave()
		return

	def login(self, widget, data=None):
		self.login_widget.set_sensitive(False)
		self.status.set_text("Connecting...")
		thread = threading.Thread(target=self.login_thread)
		thread.start()
		
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

	def main(self):
		gtk.main()
	
	def delete(self, widget, data=None):
		# ask gtk to emit the "destroy" event
		return False
	
	def destroy(self, widget, data=None):
		gtk.main_quit()

if __name__ == "__main__":
	manager = MysqlManager()
	manager.main()

