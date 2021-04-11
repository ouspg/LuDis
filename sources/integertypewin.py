#############################################################
#   Module for defining a field/subfield of integer type.   #
#   Creates a new popup window.                             #
#   Author: Jarmo Luomala (2013)                            #
#############################################################

from Tkinter import *
from tkMessageBox import showerror

from info import Info
from info import Field
from selection import *

class IntegerTypeWin(Frame):
	
	def __init__(self, parent=None):
		Frame.__init__(self, parent)
		self.main_window = self.master.master
		self.grab_set()			# grab all mouse/keyboard events in this window i.e. disable the main window
		self.master.bind('<Return>', self.on_apply)
		self.master.bind('<Escape>', self.on_cancel)
		self.WIN_WIDTH = 400
		self.WIN_HEIGHT = 500
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
		type_menu = OptionMenu(type_frame, self.field_info['type'], 'uint8', 'uint16', 'uint24', 'uint32', 'uint64', \
								'int8', 'int16', 'int24', 'int32', 'int64', 'framenum')
		type_menu.config(width=8)
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
		
		# Define description row
		desc_frame = Frame(self)
		desc_frame.pack(anchor=N, expand=YES, fill=X)
		Label(desc_frame, text='Description: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['description'] = Entry(desc_frame)
		self.field_info['description'].pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# Define base row
		base_frame = Frame(self)
		base_frame.pack(anchor=N, expand=YES, fill=X)
		Label(base_frame, text='Base: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['base'] = StringVar()
		radio1 = Radiobutton(base_frame, text='Unknown', variable=self.field_info['base'], value='UNKNOWN')
		radio1.select()
		radio1.pack(side=LEFT)
		Radiobutton(base_frame, text='DEC', variable=self.field_info['base'], value='DEC').pack(side=LEFT)
		Radiobutton(base_frame, text='HEX', variable=self.field_info['base'], value='HEX').pack(side=LEFT)
		Radiobutton(base_frame, text='OCT', variable=self.field_info['base'], value='OCT').pack(side=LEFT)
		
		# Define valuestring row
		valstr_frame = Frame(self)
		valstr_frame.pack(anchor=N, expand=YES, fill=X)
		Label(valstr_frame, text='Valuestring: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['valuestring'] = Entry(valstr_frame)
		self.field_info['valuestring'].pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# Define bitmask row
		mask_frame = Frame(self)
		mask_frame.pack(anchor=N, expand=YES, fill=X)
		Label(mask_frame, text='Bitmask: ', anchor=E, width=13).pack(side=LEFT)
		self.field_info['bitmask'] = Entry(mask_frame)
		self.field_info['bitmask'].pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# Define button row
		button_frame = Frame(self)
		button_frame.pack(anchor=S, expand=YES, pady=40)
		Button(button_frame, text='Apply', width=6, command=self.on_apply).pack(side=LEFT, padx=20)
		Button(button_frame, text='Cancel', width=6, command=self.on_cancel).pack(side=RIGHT, padx=20)

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
				showerror('Error message', 'Invalid format for field abbreviation!\n\n' +
							'Please check that you didn\'t use any dots in the abbreviation.', parent=self.master)
				return
		if self.field_info['name'].get():
			if not field.set_name(self.field_info['name'].get()):
				showerror('Error message', 'Invalid format for field name!', parent=self.master)
				return
		if self.field_info['description'].get():
			if not field.set_desc(self.field_info['description'].get()):
				showerror('Error message', 'Invalid format for field description!', parent=self.master)
				return
		if self.field_info['base'].get():
			if not field.set_base(self.field_info['base'].get()):
				showerror('Error message', 'Invalid format for field base!', parent=self.master)
				return
		if self.field_info['valuestring'].get():
			ok, err_msg = field.set_valuestring(self.field_info['valuestring'].get())
			if not ok:
				showerror('Error message', err_msg, parent=self.master)
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

		if self.field_info['bitmask'].get():
			ok, err_msg = field.set_bitmask(self.field_info['bitmask'].get())
			if not ok:
				showerror('Error message', err_msg, parent=self.master)
				return

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

		# Update the protocol tree, defined fields in the packet frame, and close the popup window.
		self.main_window.update_defined_fields()
		self.main_window.update_tree()
		self.master.destroy()


	def on_cancel(self, event=None):
		self.master.destroy()


if __name__ == '__main__':
	root = Tk()
	IntegerTypeWin(parent=root).mainloop()
