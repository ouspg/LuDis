##############################################################
#   Module for the window where the delimiters are defined.  #
#   Author: Jarmo Luomala (2013)                             #
##############################################################

from Tkinter import *
from tkMessageBox import showerror
import string

from info import Info

class DelimitersWin(Frame):
	
	def __init__(self, parent=None):
		Frame.__init__(self, parent)
		self.grab_set()			# grab all mouse/keyboard events in this window i.e. disable the main window
		self.master.bind('<Return>', self.on_apply)
		self.master.bind('<Escape>', self.on_cancel)
		self.main_window = self.master.master
		self.WIN_WIDTH = 300
		self.WIN_HEIGHT = 200
		self.WIN_OFFSET = '+525+100'
		self.master.geometry(str(self.WIN_WIDTH)+'x'+str(self.WIN_HEIGHT)+self.WIN_OFFSET)
		self.master.resizable(FALSE, FALSE)
		self.master.title('Define delimiters')
		self.pack(expand=YES, fill=BOTH)
		self.field_delim = ''
		self.subfield_delim = ''
		self.make_widgets()

	def make_widgets(self):	
		"""Make widgets for the popup window."""

		# Define field delimiter row
		field_delim_frame = Frame(self)
		field_delim_frame.pack(anchor=N, expand=YES, fill=X, pady=30)			# No padding
		Label(field_delim_frame, text='Field delimiter: ', anchor=E, width=15).pack(side=LEFT)	# width=14
		self.field_delim = Entry(field_delim_frame)
		self.field_delim.pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# Define subfield delimiter row
		subfield_delim_frame = Frame(self)
		subfield_delim_frame.pack(anchor=N, expand=YES, fill=X)
		Label(subfield_delim_frame, text='Subfield delimiter: ', anchor=E, width=15).pack(side=LEFT)	# width=14
		self.subfield_delim = Entry(subfield_delim_frame)
		self.subfield_delim.pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# Define button row
		button_frame = Frame(self)
		button_frame.pack(anchor=S, expand=YES, pady=20)
		Button(button_frame, text='Apply', width=6, command=self.on_apply).pack(side=LEFT, padx=30)
		Button(button_frame, text='Cancel', width=6, command=self.on_cancel).pack(side=RIGHT, padx=30)
		
	def check_delimiter(self, delim):
		delim = delim.replace(' ', '')
		if delim.startswith('0x'):
			array = delim.split('0x')
			if len(array) != 2:
				return (False, None)
			delim = array[1]
		if len(delim) % 2 != 0:
			return (False, None)

		for char in delim:
			if char in string.hexdigits:
				pass
			else:
				return (False, None)

		for i in range(0, len(delim), 2):
			if int(delim[i:i+2], 16) >= 32 and int(delim[i:i+2], 16) <= 126:
				pass
			# Accept only those control characters that are representable by escape sequences.
			elif (int(delim[i:i+2], 16) == 9 or int(delim[i:i+2], 16) == 10 or int(delim[i:i+2], 16) == 13):
				pass
			else:
				return (False, None)

		# Add spaces between bytes
		j = 0
		for i in range(2, len(delim), 2):
			delim = delim[0:i+j] + ' ' + delim[i+j:]
			j += 1

		return (True, delim)

	def on_apply(self, event=None):
		field_delim, subfield_delim = '', ''
		# Required fields must not be empty.
		if not self.field_delim.get() or self.field_delim.get().isspace():
			showerror('Error message', 'Field delimiter is required and must consist of valid hexadecimals!', parent=self.master)
			return

		valid, field_delim = self.check_delimiter(self.field_delim.get())
		if not valid:
			showerror('Error message', 'Invalid format for field delimiter!\n\n' +
				'Delimiters must be presented as full bytes of hexadecimal values, with or without 0x prefix ' +
				'(e.g., "0x0d0a" or "0d 0a").\nOnly the following control characters (in hex) are allowed to be used in delimiters: ' +
				'09, 0A, and 0D.', parent=self.master)
			return

		if self.subfield_delim.get():
			if self.subfield_delim.get().isspace():
				showerror('Error message', 'Subfield delimiter must consist of valid hexadecimals!', parent=self.master)
				return
			valid, subfield_delim = self.check_delimiter(self.subfield_delim.get())
			if not valid:
				showerror('Error message', 'Invalid format for subfield delimiter!\n\n' +
					'Delimiters must be presented as full bytes of hexadecimal values, with or without 0x prefix ' +
					'(e.g., "0x0d0a" or "0d 0a").\nOnly the following control characters (in hex) are allowed to be used in delimiters: ' +
					'09, 0A, and 0D.', parent=self.master)
				return

		self.main_window.field_delimiter = field_delim.upper()
		self.main_window.subfield_delimiter = subfield_delim.upper()
		Info.field_delimiter = field_delim.upper()
		Info.subfield_delimiter = subfield_delim.upper()
		self.main_window.create_delim_field_list()
		self.main_window.radioFixed.config(state=DISABLED)
		self.main_window.radioDelim.config(state=DISABLED)
		self.main_window.delimiters_btn.config(state=DISABLED)
		self.master.destroy()

	def on_cancel(self, event=None):
		"""Cancels the action and closes the popup window."""
		self.master.destroy()
		
		
if __name__ == '__main__':
	root = Tk()
	DelimitersWin(parent=root).mainloop()