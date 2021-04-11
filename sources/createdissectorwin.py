############################################################
#   Module for the window where the dissector is created.  #
#   Author: Jarmo Luomala (2013)                           #
############################################################

import os
from Tkinter import *
from tkMessageBox import showerror, askyesno
from tkFileDialog import askdirectory

from info import Info, Field
from dissector import Protocol

class CreateDissectorWin(Frame):
	
	def __init__(self, parent=None):
		Frame.__init__(self, parent)
		self.main_window = self.master.master
		self.grab_set()			# grab all mouse/keyboard events in this window i.e. disable the main window
		self.master.bind('<Return>', self.on_create)
		self.master.bind('<Escape>', self.on_cancel)
		self.WIN_WIDTH = 400
		self.WIN_HEIGHT = 400
		self.WIN_OFFSET = '+475+100'
		self.master.geometry(str(self.WIN_WIDTH)+'x'+str(self.WIN_HEIGHT)+self.WIN_OFFSET)
		self.master.resizable(FALSE, FALSE)
		self.master.title('Create protocol dissector')
		self.pack(expand=YES, fill=BOTH)
		self.dissector_info = {}
		self.directory = None
		self.file_name = None
		self.make_widgets()
			
	def make_widgets(self):
		"""Make widgets for the popup window."""
		
		# -- Required --
		req_frame = Frame(self)
		req_frame.pack(anchor=N, expand=YES, fill=X)
		Label(req_frame, text='Required information', font=('Sans', 9, 'bold')).pack(side=LEFT, padx=5, pady=10)
		
		# Define askdirectory row.
		dir_frame = Frame(self)
		dir_frame.pack(anchor=N, expand=YES, fill=X)
		Button(dir_frame, text='Save in..', command=self.select_directory, width=8).pack(side=LEFT, padx=12)
		self.directory = StringVar()
		Entry(dir_frame, textvariable=self.directory, bg='white', highlightcolor='grey').pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# -- Optional --
		opt_frame = Frame(self)
		opt_frame.pack(anchor=N, expand=YES, fill=X)
		Label(opt_frame, text='Optional information', font=('Sans', 9, 'bold'), anchor=W, width=20).pack(side=LEFT, padx=5)
		
		# Define the parent dissector (dissector table) of this dissector.
		parent_diss_frame = Frame(self)
		parent_diss_frame.pack(anchor=N, expand=YES, fill=X)
		Label(parent_diss_frame, text='Dissector table (parent): ', anchor=E, width=20).pack(side=LEFT)
		self.dissector_info['parent_diss_table'] = Entry(parent_diss_frame)
		self.dissector_info['parent_diss_table'].pack(side=RIGHT, expand=YES, fill=X, padx=5)

		# Define dissector ID (port for parent dissector/dissector table).
		id_frame = Frame(self)
		id_frame.pack(anchor=N, expand=YES, fill=X)
		Label(id_frame, text='Dissector ID (port): ', anchor=E, width=20).pack(side=LEFT)
		self.dissector_info['id'] = Entry(id_frame)
		self.dissector_info['id'].pack(side=RIGHT, expand=YES, fill=X, padx=5)

		# Define a new dissector table for this dissector.
		diss_table_frame = Frame(self)
		diss_table_frame.pack(anchor=N, expand=YES, fill=X)
		Label(diss_table_frame, text='Dissector table (new): ', anchor=E, width=20).pack(side=LEFT)
		self.dissector_info['diss_table'] = Entry(diss_table_frame)
		self.dissector_info['diss_table'].pack(side=RIGHT, expand=YES, fill=X, padx=5)

		# Define subdissector ID field.
		subdis_frame = Frame(self)
		subdis_frame.pack(anchor=N, expand=YES, fill=X)
		Label(subdis_frame, text='Subdissector ID field ', font=('Sans', 9, 'italic'), anchor=E, width=20).pack(side=LEFT)
		subdis_field_frame = Frame(self)
		subdis_field_frame.pack(anchor=N, expand=YES, fill=X)		
		# Field and subfield numbers are used if field lengths are defined by delimiters.
		Label(subdis_field_frame, text='Field: ', anchor=E, width=20).pack(side=LEFT)
		self.dissector_info['subdiss_id_field_num'] = Entry(subdis_field_frame, width=8)
		self.dissector_info['subdiss_id_field_num'].pack(side=LEFT, padx=5)
		Label(subdis_field_frame, text='Subfield: ', anchor=E, width=9).pack(side=LEFT)
		self.dissector_info['subdiss_id_subfield_num'] = Entry(subdis_field_frame, width=8)
		self.dissector_info['subdiss_id_subfield_num'].pack(side=LEFT, padx=5)
		
		# Define button row
		button_frame = Frame(self)
		button_frame.pack(anchor=S, expand=YES, pady=20)
		Button(button_frame, text='Create', width=6, command=self.on_create).pack(side=LEFT, padx=30)
		Button(button_frame, text='Cancel', width=6, command=self.on_cancel).pack(side=RIGHT, padx=30)
		
	def select_directory(self):
		dir = askdirectory(parent=self, title='Select directory')
		if dir:
			self.directory.set(dir)
		
	def on_create(self, event=None):
		# Directory must be specified.
		if not self.directory.get():
			showerror('Error message', 'Directory must be specified!', parent=self.master)
			return
		
		# If the dissector ID is specified, the parent dissector table must be given too, and vice versa.
		if self.dissector_info['id'].get() and not self.dissector_info['parent_diss_table'].get():
			showerror('Error message', 'Please define also the parent dissector table to which the given' +
						' dissector ID (port number) is related!', parent=self.master)
			return
		elif self.dissector_info['parent_diss_table'].get() and not self.dissector_info['id'].get():
			showerror('Error message', 'Please define also the dissector ID (port number) related to' + 
						' the given parent dissector table!', parent=self.master)
			return
		
		# If the new dissector table name is given, the subdissector ID field must be specified too.
		if self.dissector_info['diss_table'].get():
			if not self.dissector_info['subdiss_id_field_num'].get():
				showerror('Error message', 'If a new dissector table is to be created for the protocol, the subdissector ID field' + 
							' must be specified too!\n\nDefine the corresponding field number or both the' +
							' field and the subfield number.', parent=self.master)
				return

		# If the subdissector ID related subfield number is given, the corresponding field number must be given too.
		if self.dissector_info['subdiss_id_subfield_num'].get() and not self.dissector_info['subdiss_id_field_num'].get():
			showerror('Error message', 'Please define also the number of the field to which the given subfield number refers!',
						parent=self.master)
			return

		# Try to set the given information in Info class.
		if self.dissector_info['parent_diss_table'].get():
			if not Info.set_parent_dissector_table(self.dissector_info['parent_diss_table'].get()):
				showerror('Error message', 'Invalid format for the parent dissector table name!\n\n' + 
							'Table name must be given in lowercase letters and without any whitespaces!', parent=self.master)
				return
		
		if self.dissector_info['id'].get():
			if not Info.set_dissector_id(self.dissector_info['id'].get()):
				showerror('Error message', 'Invalid format for the dissector ID!\nOnly valid integers are allowed!', parent=self.master)
				return
		
		if self.dissector_info['diss_table'].get():
			if not Info.set_dissector_table(self.dissector_info['diss_table'].get()):
				showerror('Error message', 'Invalid format for the dissector table name!\n\n' + 
							'Table name must be given in lowercase letters and without any whitespaces!', parent=self.master)
				return

		if self.dissector_info['subdiss_id_field_num'].get():
			if not Info.set_subdiss_id_field_num(self.dissector_info['subdiss_id_field_num'].get()):
				showerror('Error message', 'Invalid format for the field number of the subdissector ID field!\n\n' +
							'Field number must be a valid nonnegative integer and smaller than' + 
							' the number of fields in the packet! In other words, the number must refer to an existing' +
							' and defined field.', parent=self.master)
				return
		
		if self.dissector_info['subdiss_id_subfield_num'].get():
			if not Info.set_subdiss_id_subfield_num(self.dissector_info['subdiss_id_subfield_num'].get()):
				showerror('Error message', 'Invalid format for the subfield number of the subdissector ID field!\n\n' +
							'Subfield number must be a valid nonnegative integer and smaller than' + 
							' the number of subfields in the specified field! In other words, the number must refer to an existing' +
							' and defined subfield.', parent=self.master)
				return


		if len(Info.get_proto_name()) > 0:
			self.file_name = Info.get_proto_name().lower().replace(' ', '_') + '.lua'
		else:
			self.file_name = 'my_proto.lua'
		
		if askyesno('Confirm', 'New Lua dissector file with name \"' + self.file_name + 
					'\" will be generated into the specified directory.\n\n' +
					'Do you want to continue?'):
			proto = Protocol()
			# Call the method that generates the actual dissector code
			lua_code = proto.generate()
			created = self.write_dissector_to_file(lua_code)
			if created:
				self.clean()
				self.master.destroy()
		else:
			return

	def write_dissector_to_file(self, lua_code):
		# Delete output file if it already exists.
		path = self.directory.get() + '/' + self.file_name
		flag = 'w' # open file in 'write' mode
		if os.path.isfile(path):
			if askyesno('Warning message', 'A file named \"' + self.file_name + '\" already exists.\nDo you want to replace it?'):
				os.remove(path)
			else:
				return False

		with open(path, flag) as f:
			f.write(lua_code)
		print 'Dissector file created in:', path
		return True

	def clean(self):
		# Clear the protocol definition.
		self.main_window.clear_protocol_info_helper()
		# Clear the delimiters if they exist.
		if self.main_window.use_delimiters:
			self.main_window.clear_delimiters()
		# Clear the packet frame.
		self.main_window.set_text(text='')

	def on_cancel(self, event=None):
		self.master.destroy()

		
if __name__ == '__main__':
	root = Tk()
	CreateDissectorWin(parent=root).mainloop()