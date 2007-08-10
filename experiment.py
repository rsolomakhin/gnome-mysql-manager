#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class MysqlManager:
	def __init__(self):
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
		
		self.hostEntry.connect("key-release-event", self.update_login_widget)
		self.userEntry.connect("key-release-event", self.update_login_widget)

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

	def login(self, widget, data=None):
		errors = 0
		if self.hostEntry.get_text() == "":
			errors = errors+1
		if self.userEntry.get_text() == "":
			errors = errors+1
		if errors > 0:
			return
		view = gtk.TreeView()
		title = self.userEntry.get_text()+"@"+self.hostEntry.get_text()+":"+str(int(self.portAdjst.get_value()))
		self.notebook.prepend_page(view, gtk.Label(title))
		view.show_all()
		self.notebook.set_current_page(0)
		
	def update_login_widget(self, widget, event):
		red = gtk.gdk.color_parse("red")
		white = gtk.gdk.color_parse("white")
		errors = 0
		if self.hostEntry.get_text() == "":
			self.hostEntry.modify_base(gtk.STATE_NORMAL, red)
			errors += 1
		else:
			self.hostEntry.modify_base(gtk.STATE_NORMAL, white)
		if self.userEntry.get_text() == "":
			self.userEntry.modify_base(gtk.STATE_NORMAL, red)
			errors += 1
		else:
			self.userEntry.modify_base(gtk.STATE_NORMAL, white)
		self.login_button.set_sensitive(errors == 0)

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

