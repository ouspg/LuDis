############################################
#   Module for defining a field/subfield   #
#   of other type than integer.            #
#   Creates a new popup window.            #
#   Author: Jarmo Luomala (2013)           #
############################################

from Tkinter import *
from tkMessageBox import showerror

from info import Info
from info import Field
from selection import *

class OtherTypeWin(Frame):
	
	def __init__(self, parent=None):
		Frame.__init__(self, parent)
		self.grab_set()			# grab all mouse/keyboard events in this window i.e. disable the main window
		self.master.bind('<Return>', self.on_apply)
		self.master.bind('<Escape>', self.on_cancel)
		self.main_window = self.master.master
		self.WIN_WIDTH = 400
		self.WIN_HEIGHT = 350
		self.WIN_OFFSET = '+475+100'
		self.master.geometry(str(self.WIN_WIDTH)+'x'+str(self.WIN_HEIGHT)+self.WIN_OFFSET)
		self.master.resizable(FALSE, FALSE)
		self.master.title('Define field information')
		self.pack(expand=YES, fill=BOTH)
		self.field_info = {}
		self.make_widgets()
		
	def make_widgets(self):	
		"""Make widgets for the popup window."""
		
		# -- Required --
		req_frame = Frame(self)
		req_frame.pack(anchor=N, expand=YES, fill=X)
		Label(req_frame, text='Required information', font=('Sans', 9, 'bold'), anchor=W).pack(side=LEFT, padx=5, pady=10)
		
		# Define type row
		type_frame = Frame(self)
		type_frame.pack(anchor=N, expand=YES)
		Label(type_frame, text='Type: ').pack(side=LEFT, padx=20)
		self.field_info['type'] = StringVar()
		optionList = ('float', 'double', 'string', 'stringz', 'bytes', 'ubytes', 'bool', 'ipv4', 'ipv6', \
					  'ether', 'ipxnet', 'absolute_time', 'relative_time', 'pcre', 'oid', 'guid', 'eui64')
		type_menu = OptionMenu(type_frame, self.field_info['type'], *optionList)
								
		for i in range(17):
			type_menu['menu'].entryconfig(i, label=optionList[i], command=lambda type=optionList[i]: self.check_base_field(type))

		type_menu.config(width=10)
		type_menu.pack(side=RIGHT, padx=20)
		
		# Define abbreviation row
		abbr_frame = Frame(self)
		abbr_frame.pack(anchor=N, expand=YES, fill=X, pady=15)
		Label(abbr_frame, text='Abbreviation: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['abbreviation'] = Entry(abbr_frame)
		self.field_info['abbreviation'].pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# -- Optional --
		opt_frame = Frame(self)
		opt_frame.pack(anchor=N, expand=YES, fill=X)
		Label(opt_frame, text='Optional information', font=('Sans', 9, 'bold'), anchor=W, width=20).pack(side=LEFT, padx=5)
		
		# Define name row
		name_frame = Frame(self)
		name_frame.pack(anchor=N, expand=YES, fill=X)
		Label(name_frame, text='Name: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['name'] = Entry(name_frame)
		self.field_info['name'].pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# Define base row
		base_frame = Frame(self)
		base_frame.pack(anchor=N, expand=YES, fill=X)
		Label(base_frame, text='Base: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['base'] = StringVar()
		self.radio1 = Radiobutton(base_frame, text='Unknown', variable=self.field_info['base'], value='UNKNOWN', state=DISABLED)
		self.radio1.select()
		self.radio1.pack(side=LEFT)
		self.radio2 = Radiobutton(base_frame, text='LOCAL', variable=self.field_info['base'], value='LOCAL', state=DISABLED)
		self.radio2.pack(side=LEFT)
		self.radio3 = Radiobutton(base_frame, text='UTC', variable=self.field_info['base'], value='UTC', state=DISABLED)
		self.radio3.pack(side=LEFT)
		self.radio4 = Radiobutton(base_frame, text='DOY_UTC', variable=self.field_info['base'], value='DOY_UTC', state=DISABLED)
		self.radio4.pack(side=LEFT)
		self.base_frame = base_frame
		
		# Define description row
		desc_frame = Frame(self)
		desc_frame.pack(anchor=N, expand=YES, fill=X)
		Label(desc_frame, text='Description: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['description'] = Entry(desc_frame)
		self.field_info['description'].pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		button_frame = Frame(self)
		button_frame.pack(anchor=S, expand=YES, pady=40)
		Button(button_frame, text='Apply', width=6, command=self.on_apply).pack(side=LEFT, padx=30)
		Button(button_frame, text='Cancel', width=6, command=self.on_cancel).pack(side=RIGHT, padx=30)
		
	def check_base_field(self, type):
		self.field_info['type'].set(type)
		# Enable base field, if absolute_time chosen.
		if type == 'absolute_time':
			self.radio1.config(state=NORMAL)
			self.radio2.config(state=NORMAL)
			self.radio3.config(state=NORMAL)
			self.radio4.config(state=NORMAL)
		else:
			self.radio1.config(state=DISABLED)
			self.radio2.config(state=DISABLED)
			self.radio3.config(state=DISABLED)
			self.radio4.config(state=DISABLED)
		
	def on_apply(self, event=None):
		# Type and abbreviation fields must not be empty.
		if not self.field_info['type'].get():
			showerror('Error message', 'Type field is required!', parent=self.master)
			return
		elif not self.field_info['abbreviation'].get():
			showerror('Error message', 'Abbreviation field is required!', parent=self.master)
			return

		field = Field()
		if self.field_info['type'].get():
			if not field.set_type(self.field_info['type'].get()):
				showerror('Error message', 'Invalid format for field type!', parent=self.master)
				return
		if self.field_info['abbreviation'].get():
			if not field.set_abbr(self.field_info['abbreviation'].get()):
				showerror('Error message', 'Invalid format for field abbreviation!', parent=self.master)
				return
		if self.field_info['name'].get():
			if not field.set_name(self.field_info['name'].get()):
				showerror('Error message', 'Invalid format for field name!', parent=self.master)
				return
		if self.field_info['base'].get():
			if not field.set_base(self.field_info['base'].get()):
				showerror('Error message', 'Invalid format for field base!', parent=self.master)
				return
		if self.field_info['description'].get():
			if not field.set_desc(self.field_info['description'].get()):
				showerror('Error message', 'Invalid format for field description!', parent=self.master)
				return

		start, end = 0, 0
		# Fields have fixed lengths.
		if not self.main_window.use_delimiters:
			if self.main_window.show_in == 'BIN':
				start, end = sel_from_bin(self.main_window.sel_first, self.main_window.sel_last)
			elif self.main_window.show_in == 'HEX':
				start, end = sel_from_hex(self.main_window.sel_first, self.main_window.sel_last)
			elif self.main_window.show_in == 'ASCII':
				start, end = sel_from_ascii(self.main_window.sel_first, self.main_window.sel_last)
		# Fields are separated by delimiters.
		else:
			if len(self.main_window.text.tag_ranges('DELIM_SUBFIELD')) > 0:
				start, end = self.main_window.text.tag_ranges('DELIM_SUBFIELD')
				start_str, end_str = str(start), str(end)
				# Mark the subfield as "defined" in the corresp. table.
				for tbl in self.main_window.subfield_borders:
					field_index = self.main_window.subfield_borders.index(tbl)
					try:
						subfield_index = tbl.index([start_str, end_str])
						Info.defined_delim_subfields[field_index][subfield_index] = True
						break
					except ValueError:
						pass
				start, end = sel_from_hex(start, end)
			else:
				start, end = self.main_window.text.tag_ranges('DELIM_FIELD')
				start_str, end_str = str(start), str(end)
				# Mark the field as "defined" in the corresp. table.
				index = self.main_window.field_borders.index([start_str, end_str])
				Info.defined_delim_fields[index] = True
				start, end = sel_from_hex(start, end)

		field.set_start(start)
		field.set_end(end)

		sel_start, sel_end = nibbles_to_sel(2 * start, 2 * end + 1, self.main_window.show_in)
		if sel_start and sel_end:
			if not field.set_value(self.main_window.text.get(sel_start, sel_end), self.main_window.show_in):
				showerror('Error message', 'Could not set the field value!', parent=self.master)
				return

		if not Info.add_field(field):
			showerror('Error message', 'Field could not be defined!\n\n' + 
						'Please check that the field is highlighted rationally. ' +
						'Note that fields can have subfields only on one level.', parent=self.master)
			return

		# Update the table containing areas that are tagged with 'DEFINED'.
		for format in ['BIN', 'HEX', 'ASCII']:
			first, last = nibbles_to_sel(field.get_start() * 2, field.get_end() * 2 + 1, format)
			self.main_window.defined_table[format].append((first, last))

		# DEBUG: Print all defined fields to the console.
		# for key, val in self.field_info.items():
		# 	print "%s: %s" % (key, val.get())

		# Update the protocol tree, defined fields in the packet frame, and close the popup window.
		self.main_window.update_defined_fields()
		self.main_window.update_tree()
		self.master.destroy()


	def on_cancel(self, event=None):
		self.master.destroy()


if __name__ == '__main__':
	root = Tk()
	OtherTypeWin(parent=root).mainloop()
