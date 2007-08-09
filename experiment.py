#!/usr/bin/env python

import pygtk
pygtk.require('2.0')
import gtk

class MysqlManager:
	def __init__(self):
		self.login_widget = None
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.connect("delete_event", self.delete)
		self.window.connect("destroy", self.destroy)
		self.notebook = gtk.Notebook()
		self.notebook.set_tab_pos(gtk.POS_LEFT)
		self.notebook.append_page(self.get_login_widget(), gtk.Label("Login"))
		self.window.add(self.notebook)
		self.window.show_all()

	def get_login_widget(self):
		if self.login_widget == None:
			self.login_widget = gtk.VBox()
			self.hostEntry = gtk.Entry()
			self.portEntry = gtk.Entry()
			self.userEntry = gtk.Entry()
			self.passEntry = gtk.Entry()

			box = gtk.HBox()
			box.add(gtk.Label("Host:"))
			box.add(self.hostEntry)
			self.login_widget.add(box)

			box = gtk.HBox()
			box.add(gtk.Label("Port:"))
			box.add(self.portEntry)
			self.login_widget.add(box)
			
			box = gtk.HBox()
			box.add(gtk.Label("User:"))
			box.add(self.userEntry)
			self.login_widget.add(box)

			box = gtk.HBox()
			box.add(gtk.Label("Password:"))
			box.add(self.passEntry)
			self.login_widget.add(box)

			button = gtk.Button("Login")
			button.connect("clicked", self.login)
			self.login_widget.add(button)
			
		return self.login_widget

	def login(self, widget, data=None):
		view = gtk.TreeView()
		title = self.userEntry.get_text()+"@"+self.hostEntry.get_text()+":"+self.portEntry.get_text()
		self.notebook.prepend_page(view, gtk.Label(title))
		view.show_all()
		self.notebook.set_current_page(0)
		
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

