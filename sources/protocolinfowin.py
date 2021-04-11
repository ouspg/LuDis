#####################################################
#   Module for defining the protocol information.   #
#   Creates a new popup window.                     #
#   Author: Jarmo Luomala (2013)                    #
#####################################################

from Tkinter import *
from tkMessageBox import showerror
import binascii
import string

from info import Info

class ProtocolInfoWin(Frame):
	
	def __init__(self, parent=None):
		Frame.__init__(self, parent)
		self.grab_set()			# grab all mouse/keyboard events in this window i.e. disable the main window
		self.master.bind('<Return>', self.on_apply)
		self.master.bind('<Escape>', self.on_cancel)
		self.main_window = self.master.master
		self.WIN_WIDTH = 400
		self.WIN_HEIGHT = 470 # 200
		self.WIN_OFFSET = '+475+100'
		self.master.geometry(str(self.WIN_WIDTH)+'x'+str(self.WIN_HEIGHT)+self.WIN_OFFSET)
		self.master.resizable(FALSE, FALSE)
		self.master.title('Define protocol information')
		self.pack(expand=YES, fill=BOTH)
		self.proto_info = {}
		self.len_header = None
		self.len_data = None
		self.make_widgets()
			
	def make_widgets(self):	
		"""Make widgets for the popup window."""
		
		#-- Required --		
		# Define name row
		name_frame = Frame(self)
		name_frame.pack(anchor=S, expand=YES, fill=X, pady=15)					# No padding
		Label(name_frame, text='Name: ', anchor=E, width=13).pack(side=LEFT)	# width=14
		self.proto_info['name'] = Entry(name_frame)
		self.proto_info['name'].pack(side=RIGHT, expand=YES, fill=X, padx=5)
		
		# Define description row
		desc_frame = Frame(self)
		desc_frame.pack(anchor=N, expand=YES, fill=X, pady=5)
		Label(desc_frame, text='Description: ', anchor=E, width=13).pack(side=LEFT)	# width=14
		self.proto_info['description'] = Entry(desc_frame)
		self.proto_info['description'].pack(side=RIGHT, expand=YES, fill=X, padx=5)

		# Define header length row
		header_frame = Frame(self)
		header_frame.pack(anchor=N, expand=YES, fill=X, pady=10)
		header_subframe1 = Frame(header_frame)
		header_subframe1.pack(anchor=W, expand=YES, fill=Y)
		header_subframe2 = Frame(header_frame)
		header_subframe2.pack(side=TOP)
		header_subframe3 = Frame(header_frame)
		header_subframe3.pack(side=TOP)
		header_subframe4 = Frame(header_frame)
		header_subframe4.pack(side=TOP)

		#-- Header length --
		Label(header_subframe1, text='Header length: ', anchor=E, width=13).pack(side=LEFT)
		self.header_type = StringVar()

		# Limit header length according to the last header field
		header_last_btn = Radiobutton(header_subframe2, text='Use end of the last header field', width=25,
									   variable=self.header_type, value='LAST', anchor=W,
									   command=self.toggle_header_type)
		header_last_btn.select()
		header_last_btn.pack(anchor=W)

		# Use given length
		header_given_btn = Radiobutton(header_subframe3, text='Use given length', width=25,
									   variable=self.header_type, value='GIVEN', anchor=W,
									   command=self.toggle_header_type)
		#header_given_btn.select()
		header_given_btn.pack(anchor=W)
		Label(header_subframe3, text='      Number of bytes: ', anchor=E).pack(side=LEFT)
		self.header_length = Entry(header_subframe3, width=10)
		self.header_length.pack(side=LEFT)
		self.header_length.config(state=DISABLED)
		
		# Use delimiter
		header_delim_btn = Radiobutton(header_subframe4, text='Use delimiter', width=25, variable=self.header_type,
									   value='DELIM', anchor=W, command=self.toggle_header_type)
		header_delim_btn.pack(anchor=W)
		Label(header_subframe4, text='      Delimiter: ', anchor=E).pack(side=LEFT)
		self.header_delimiter = Entry(header_subframe4, width=10)
		self.header_delimiter.pack(side=LEFT)
		self.header_delimiter.config(state=DISABLED)

		# Define payload length row
		data_frame = Frame(self)
		data_frame.pack(anchor=N, expand=YES, fill=X)
		data_subframe1 = Frame(data_frame)
		data_subframe1.pack(anchor=W, expand=YES, fill=Y)
		data_subframe2 = Frame(data_frame)
		data_subframe2.pack(side=TOP)
		data_subframe3 = Frame(data_frame)
		data_subframe3.pack(side=TOP)
		data_subframe4 = Frame(data_frame)
		data_subframe4.pack(side=TOP)
		data_subframe5 = Frame(data_frame)
		data_subframe5.pack(side=TOP)
		data_subframe6 = Frame(data_frame)
		data_subframe6.pack(side=TOP)

		#-- Payload length --
		Label(data_subframe1, text='Payload length: ', anchor=E, width=13).pack(side=LEFT)
		self.data_type = StringVar()

		data_rest_btn = Radiobutton(data_subframe2, text='Use all bytes after the header', width=25,
									   variable=self.data_type, value='REST', anchor=W,
									   command=self.toggle_data_type)
		data_rest_btn.select()
		data_rest_btn.pack(anchor=W)
		
		# Use delimiter
		data_delim_btn = Radiobutton(data_subframe4, text='Use delimiter', width=25, variable=self.data_type,
									   value='DELIM', anchor=W, command=self.toggle_data_type)
		data_delim_btn.pack(anchor=W)
		Label(data_subframe4, text='      Delimiter: ', anchor=E).pack(side=LEFT)
		self.data_delimiter = Entry(data_subframe4, width=10)
		self.data_delimiter.pack(side=LEFT)
		self.data_delimiter.config(state=DISABLED)

		# Use header field
		data_field_btn = Radiobutton(data_subframe5, text='Use header field', width=25, variable=self.data_type,
									   value='FIELD', anchor=W, command=self.toggle_data_type)
		data_field_btn.pack(anchor=W)
		Label(data_subframe6, text='Field: ', anchor=E, width=15).pack(side=LEFT)
		self.data_field = Entry(data_subframe6, width=8)
		self.data_field.pack(side=LEFT, padx=5)
		self.data_field.config(state=DISABLED)
		Label(data_subframe6, text='Subfield: ', anchor=E).pack(side=LEFT)
		self.data_subfield = Entry(data_subframe6, width=8)
		self.data_subfield.pack(side=LEFT, padx=5)
		self.data_subfield.config(state=DISABLED)
		
		#-- Optional --
		# Define button row
		button_frame = Frame(self)
		button_frame.pack(anchor=S, expand=YES, pady=20)
		Button(button_frame, text='Apply', width=6, command=self.on_apply).pack(side=LEFT, padx=30)
		Button(button_frame, text='Cancel', width=6, command=self.on_cancel).pack(side=RIGHT, padx=30)
		

	def toggle_header_type(self):
		if self.header_type.get() == 'LAST':
			self.header_length.delete(0, END)
			self.header_length.config(state=DISABLED)
			self.header_delimiter.delete(0, END)
			self.header_delimiter.config(state=DISABLED)
		elif self.header_type.get() == 'GIVEN':
			self.header_delimiter.delete(0, END)
			self.header_delimiter.config(state=DISABLED)
			self.header_length.config(state=NORMAL)
		elif self.header_type.get() == 'DELIM':
			self.header_length.delete(0, END)
			self.header_length.config(state=DISABLED)
			self.header_delimiter.config(state=NORMAL)

	def toggle_data_type(self):
		if self.data_type.get() == 'REST':
			self.data_delimiter.delete(0, END)
			self.data_delimiter.config(state=DISABLED)
			self.data_field.delete(0, END)
			self.data_field.config(state=DISABLED)
			self.data_subfield.delete(0, END)
			self.data_subfield.config(state=DISABLED)
		elif self.data_type.get() == 'DELIM':
			self.data_field.delete(0, END)
			self.data_field.config(state=DISABLED)
			self.data_subfield.delete(0, END)
			self.data_subfield.config(state=DISABLED)
			self.data_delimiter.config(state=NORMAL)
		elif self.data_type.get() == 'FIELD':
			self.data_delimiter.delete(0, END)
			self.data_delimiter.config(state=DISABLED)
			self.data_field.config(state=NORMAL)
			self.data_subfield.config(state=NORMAL)

	def check_header_length(self, length):
		if not length.isdigit():
			return False
		if len(length) > 1 and length.startswith('0'):
			return False
		else:
			length = int(length)
		# Header must be at least one byte long
		if not length > 0:
			return False

		# Get the sample packet length in bytes
		packet = self.main_window.get_text()
		if self.main_window.show_in == 'BIN':
			num_bytes = len(packet.replace(' ', '')) / 8
		elif self.main_window.show_in == 'HEX':
			num_bytes = len(packet.replace(' ', '')) / 2
		elif self.main_window.show_in == 'ASCII':
			num_bytes = len(packet)

		if (num_bytes - length) < 0:
			return False

		Info.header_length = length
		return True

	def check_header_delimiter(self, delim):
		delim = delim.replace(' ', '')
		if delim.startswith('0x'):
			array = delim.split('0x')
			if len(array) != 2:
				return False
			delim = array[1]
		if len(delim) % 2 != 0:
			return False
		# Set the delimiter to uppercase
		delim = delim.upper()

		# Check that characters are valid hexadecimals
		for char in delim:
			if char in string.hexdigits:
				pass
			else:
				return False

		# Check that characters are valid ASCII
		for i in range(0, len(delim), 2):
			if int(delim[i:i+2], 16) >= 32 and int(delim[i:i+2], 16) <= 126:
				pass
			# Accept only those control characters that are representable by escape sequences.
			elif (int(delim[i:i+2], 16) == 9 or int(delim[i:i+2], 16) == 10 or int(delim[i:i+2], 16) == 13):
				pass
			else:
				return False

		# Check that the delimiter is found inside the sample packet
		found = 0
		index = None
		if self.main_window.show_in == 'BIN':
			packet = self.main_window.get_text()
			delim_bin = bin(int(delim, 16))[2:]
			delim_bin = delim_bin.zfill(len(delim) * 4)		# fill with zeros to full bytes
			# Add spaces to the delimiter to correspond the sample packet spacing
			j = 0
			for i in range(8, len(delim_bin), 8):
				delim_bin = delim_bin[0:i+j] + ' ' + delim_bin[i+j:]
				j += 1
			found = packet.count(delim_bin)
			# If the delimiter was found in the packet, store the byte index
			if found > 0:
				index = packet.find(delim_bin) / 9
		elif self.main_window.show_in == 'HEX':
			packet = self.main_window.get_text()
			delim_hex = delim
			# Add spaces to the delimiter to correspond the sample packet spacing
			j = 0
			for i in range(2, len(delim_hex), 2):
				delim_hex = delim_hex[0:i+j] + ' ' + delim_hex[i+j:]
				j += 1
			found = packet.count(delim_hex)
			# If the delimiter was found in the packet, store the byte index
			if found > 0:
				index = packet.find(delim_hex) / 3
		elif self.main_window.show_in == 'ASCII':
			delim_hex = delim
			if self.main_window.text_content != '':
				# In this case the packet content is hexadecimals
				packet = self.main_window.text_content
				# Add spaces to the packet data and the delimiter (to separate bytes)
				j = 0
				for i in range(2, len(packet), 2):
					packet = packet[0:i+j] + ' ' + packet[i+j:]
					j += 1
				j = 0
				for i in range(2, len(delim_hex), 2):
					delim_hex = delim_hex[0:i+j] + ' ' + delim_hex[i+j:]
					j += 1
				found = packet.count(delim_hex)
				# If the delimiter was found in the packet, store the byte index
				if found > 0:
					index = packet.find(delim_hex) / 3
			elif self.main_window.orig_ascii != '':
				# In this case the packet content is ASCII
				packet = self.main_window.orig_ascii
				found = packet.count(binascii.unhexlify(delim))
				# If the delimiter was found in the packet, store the byte index
				if found > 0:
					index = packet.find(binascii.unhexlify(delim))

		if found == 1:
			pass
		# Delimiter can appear twice in the packet only if
		# the delimiter of the payload is the same.
		elif found == 2:
			if self.data_delimiter.get():
				temp = self.data_delimiter.get().replace(' ', '')
				if temp.startswith('0x'):
					temp = temp.split('0x')[1]

				if delim.replace(' ', '') == temp.upper():
					pass
				else:
					return False
			else:
				return False
		else:
			return False

		# Add spaces between bytes
		j = 0
		for i in range(2, len(delim), 2):
			delim = delim[0:i+j] + ' ' + delim[i+j:]
			j += 1

		Info.header_delimiter = [delim, index]
		return True

	def check_data_delimiter(self, delim):
		delim = delim.replace(' ', '')
		if delim.startswith('0x'):
			array = delim.split('0x')
			if len(array) != 2:
				return False
			delim = array[1]
		if len(delim) % 2 != 0:
			return False
		# Set the delimiter to uppercase
		delim = delim.upper()

		# Check that characters are valid hexadecimals
		for char in delim:
			if char in string.hexdigits:
				pass
			else:
				return False

		# Check that characters are valid ASCII
		for i in range(0, len(delim), 2):
			if int(delim[i:i+2], 16) >= 32 and int(delim[i:i+2], 16) <= 126:
				pass
			# Accept only those control characters that are representable by escape sequences.
			elif (int(delim[i:i+2], 16) == 9 or int(delim[i:i+2], 16) == 10 or int(delim[i:i+2], 16) == 13):
				pass
			else:
				return False

		# Check that the delimiter is found inside the sample packet
		found = 0
		index = None
		if self.main_window.show_in == 'BIN':
			packet = self.main_window.get_text()
			#packet = packet.replace(' ', '')
			delim_bin = bin(int(delim, 16))[2:]
			delim_bin = delim_bin.zfill(len(delim) * 4)		# fill with zeros to full bytes
			# Add spaces to the delimiter to correspond the sample packet spacing
			j = 0
			for i in range(8, len(delim_bin), 8):
				delim_bin = delim_bin[0:i+j] + ' ' + delim_bin[i+j:]
				j += 1
			found = packet.count(delim_bin)
			# If the delimiter was found in the packet, store the byte index
			if found > 0:
				index = packet.find(delim_bin) / 9
				if found == 2:
					index = packet.find(delim_bin, index * 9 + 1) / 9
		elif self.main_window.show_in == 'HEX':
			packet = self.main_window.get_text()
			delim_hex = delim
			# Add spaces to the delimiter to correspond the sample packet spacing
			j = 0
			for i in range(2, len(delim_hex), 2):
				delim_hex = delim_hex[0:i+j] + ' ' + delim_hex[i+j:]
				j += 1
			found = packet.count(delim_hex)
			# If the delimiter was found in the packet, store the byte index
			if found > 0:
				index = packet.find(delim_hex) / 3
				if found == 2:
					index = packet.find(delim_hex, index * 3 + 1) / 3
		elif self.main_window.show_in == 'ASCII':
			delim_hex = delim
			if self.main_window.text_content != '':
				# In this case the packet content is hexadecimals
				packet = self.main_window.text_content
				# Add spaces to the packet data and the delimiter (to separate bytes)
				j = 0
				for i in range(2, len(packet), 2):
					packet = packet[0:i+j] + ' ' + packet[i+j:]
					j += 1
				j = 0
				for i in range(2, len(delim_hex), 2):
					delim_hex = delim_hex[0:i+j] + ' ' + delim_hex[i+j:]
					j += 1
				found = packet.count(delim_hex)
				# If the delimiter was found in the packet, store the byte index
				if found > 0:
					index = packet.find(delim_hex) / 3
					if found == 2:
						index = packet.find(delim_hex, index * 3 + 1) / 3
			elif self.main_window.orig_ascii != '':
				# In this case the packet content is ASCII
				packet = self.main_window.orig_ascii
				found = packet.count(binascii.unhexlify(delim))
				# If the delimiter was found in the packet, store the byte index
				if found > 0:
					index = packet.find(delim)
					if found == 2:
						index = packet.find(delim, index + 1)

		if found == 1:
			pass
		elif found == 2:
			if self.header_delimiter.get():
				temp = self.header_delimiter.get().replace(' ', '')
				if temp.startswith('0x'):
					temp = temp.split('0x')[1]

				if delim.replace(' ', '') == temp.upper():
					pass
				else:
					return False
			else:
				return False
		else:
			return False

		# Check that the payload delimiter is after the header
		if self.header_type.get() == 'GIVEN' and Info.header_length:
			if index < Info.header_length:
				return False
		elif self.header_type.get() == 'DELIM' and Info.header_delimiter:
			if index <= (Info.header_delimiter[1] + len(Info.header_delimiter[0]) - 1):
				return False

		# Add spaces between bytes
		j = 0
		for i in range(2, len(delim), 2):
			delim = delim[0:i+j] + ' ' + delim[i+j:]
			j += 1
		
		Info.payload_delimiter = [delim, index]
		return True

	def check_data_byte_indices(self, bytes):
		if len(bytes) == 0 or bytes.isspace():
			return False
		indices = bytes.split('-')
		if len(indices) <= 2:
			for index in indices:
				if index.isdigit():
					if len(index) > 1 and index.startswith('0'):
						return False
				else:
					return False
			if len(indices) == 2 and int(indices[0]) > int(indices[1]):
				return False
			else:
				indices[0] = int(indices[0])
				indices[1] = int(indices[1])
				# Check that the bytes indicating the payload length are
				# in fact inside the header.
				if self.header_type.get() == 'GIVEN' and Info.header_length:
					if indices[1] >= Info.header_length:
						return False
				elif self.header_type.get() == 'DELIM' and Info.header_delimiter:
					if indices[1] >= Info.header_delimiter[1]:
						return False

				Info.payload_length_bytes = indices
				return True
		else:
			return False

	def check_data_length_field(self, field_num):
		# Field number mustn't start with 0, if other numbers follow.
		if len(field_num) > 1 and field_num.startswith('0'):
			return False
		# Check that the input consists of digits only. Takes also care of rejecting negative numbers.
		if not field_num.isdigit():
			return False
		Info.payload_length_field_num = int(field_num)
		return True

	def check_data_length_subfield(self, subfield_num):
		# Subfield number mustn't start with 0, if other numbers follow.
		if len(subfield_num) > 1 and subfield_num.startswith('0'):
			return False
		# Check that the input consists of digits only. Takes also care of rejecting negative numbers.
		if not subfield_num.isdigit():
			return False
		Info.payload_length_subfield_num = int(subfield_num)
		return True

#####################################
#   Apply & Cancel button methods   #
#####################################

	def on_apply(self, event=None):
		# Required fields must not be empty.
		if not self.proto_info['name'].get():
			showerror('Error message', 'Name field is required!', parent=self.master)
			return
		elif not self.proto_info['description'].get():
			showerror('Error message', 'Description field is required!', parent=self.master)
			return
		# If the subfield number is given, the corresponding field number must be given too.
		if self.data_type.get() == 'FIELD' and self.data_subfield.get() and not self.data_field.get():
			showerror('Error message', 'Please define also the number of the field to which the given subfield number refers!',
						parent=self.master)
			return

		if self.proto_info['name'].get():
			if not Info.set_proto_name(self.proto_info['name'].get()):
				showerror('Error message', 'Invalid format for name!', parent=self.master)
				return
		if self.proto_info['description'].get():
			if not Info.set_proto_desc(self.proto_info['description'].get()):
				showerror('Error message', 'Invalid format for description!', parent=self.master)
				return

		## Header length checks ##
		# Case: Use end of the last header field
		if self.header_type.get() == 'LAST':
			Info.header_length_from_last_field = True
		# Case: Use given length (number of bytes)
		elif self.header_type.get() == 'GIVEN':
			if not self.header_length.get():
				showerror('Error message', 'Header length must be specified!', parent=self.master)
				return
			if not self.check_header_length(self.header_length.get()):
				showerror('Error message', 'Invalid format for header length!\n\n' +
							'Header length must be given as a valid integer.', parent=self.master)
				return
		# Case: Use delimiter
		elif self.header_type.get() == 'DELIM':
			if not self.header_delimiter.get():
				showerror('Error message', 'Header delimiter must be specified!', parent=self.master)
				return
			if not self.check_header_delimiter(self.header_delimiter.get()):
				showerror('Error message', 'Invalid format for header delimiter!\n\n' +
							'Delimiter must be given as valid hexadecimals (with or without 0x prefix).\n' +
							'Only the following control characters (in hex) are allowed to be used in delimiters: ' +
							'09, 0A, and 0D.\n' +
							'The delimiter can appear twice in the packet only if the payload delimiter is exactly the same, ' +
							'otherwise it must not appear more than once.', parent=self.master)
				return

		## Payload length checks ##
		# Case: Use all bytes after the header
		if self.data_type.get() == 'REST':
			Info.payload_length_use_rest = True
		# Case: Use delimiter
		elif self.data_type.get() == 'DELIM':
			if not self.data_delimiter.get():
				showerror('Error message', 'Payload delimiter must be specified!', parent=self.master)
				return
			if not self.check_data_delimiter(self.data_delimiter.get()):
				showerror('Error message', 'Invalid format for payload delimiter!\n\n' +
							'Delimiter must be given as valid hexadecimals (with or without 0x prefix).\n' +
							'Only the following control characters (in hex) are allowed to be used in delimiters: ' +
							'09, 0A, and 0D.\n' +
							'The delimiter can appear twice in the packet only if the header delimiter is exactly the same, ' +
							'otherwise it must not appear more than once.', parent=self.master)
				return
		# Case: Use header field (field number)
		elif self.data_type.get() == 'FIELD':
			if not self.data_field.get():
				showerror('Error message', 'Field number must be specified!', parent=self.master)
				return
			if not self.check_data_length_field(self.data_field.get()):
				showerror('Error message', 'Invalid format for header field number!\n\n' +
							'Field number must be given as a valid integer (field numbers start from 0).', parent=self.master)
				return
			if self.data_subfield.get():
				if not self.check_data_length_subfield(self.data_subfield.get()):
					showerror('Error message', 'Invalid format for header subfield number!\n\n' +
							'Subfield number must be given as a valid integer (subfield numbers start from 0).', parent=self.master)
					return

		self.main_window.update_tree()
		self.master.destroy()


	def on_cancel(self, event=None):
		self.master.destroy()
		
		
if __name__ == '__main__':
	root = Tk()
	ProtocolInfoWin(parent=root).mainloop()