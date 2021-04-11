#!/usr/bin/python
# -*- coding: utf-8 -*-

##############################################################################
#   Main module of the Lua Dissector Generator aka LuDis                     #
#   Author: Jarmo Luomala (2013)                                             #
#   Summary: This tool is the empirical part of the Master's thesis titled   #
#   "A tool for generating protocol dissectors for Wireshark in Lua", which  #
#   was conducted in the Department of Computer Science and Engineering, at  #
#   the University of Oulu, Finland.                                         #
#   The thesis can be found at: http://urn.fi/URN:NBN:fi:oulu-201312021942   #
##############################################################################

# Include libraries
from Tkinter import *
from tkSimpleDialog import askstring
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import showerror, showinfo, askyesno
import binascii	# Binary and ASCII conversions
import re		# Regular expressions

# Include own files
from quitter import Quitter
from helpwin import HelpWin
from protocolinfowin import ProtocolInfoWin
from integertypewin import IntegerTypeWin
from othertypewin import OtherTypeWin
from delimiterswin import DelimitersWin
from createdissectorwin import CreateDissectorWin
from checkfile import check_file
from selection import *
from info import Info


class LuDis(Frame):
	"""The main class of the Lua Dissector Generator."""

	def __init__(self, parent=None, text='', file=None):
		"""Initializes the LuDis GUI."""
		if parent:
			parent.title('LuDis - Lua Dissector Generator')
		Frame.__init__(self, parent)
		self.pack(expand=YES, fill=BOTH)
		self.make_widgets()
		self.show_in = ''
		self.orig_ascii = ''
		self.text_content = ''
		self.defined_table = {'BIN': [], 'HEX': [], 'ASCII': []}
		self.field_delimiter = ''
		self.subfield_delimiter = ''
		self.field_borders = []
		self.subfield_borders = []
		self.delim_field_num = 0
		self.delim_subfield_num = -1 	# Not 0, because ">" button would not choose the 1st subfield
		self.use_delimiters = False
		self.set_text(text, file)
		
	def make_widgets(self):	
		"""Make widgets for the main GUI window."""
		
		# Define top frame contents
		top_frame = Frame(self)
		top_frame.pack(anchor=N, expand=YES, fill=X, padx=5, pady=5)
		Button(top_frame, text='Open', width=4, bg='gray80', command=self.on_open).pack(side=LEFT, padx=5, pady=5)
		self.save_btn = Button(top_frame, text='Save', width=4, bg='gray80', command=self.on_save_tree)
		self.save_btn.pack(side=LEFT, pady=5)
		self.save_btn.config(state=DISABLED)
		Button(top_frame, text='Help', width=4, bg='gray80', command=self.on_help).pack(side=LEFT, padx=5, pady=5)
		Quitter(top_frame).pack(side=LEFT, pady=5)
		
		# Define middle frame contents
		middle_frame = Frame(self)
		middle_frame.pack(side=TOP, expand=YES, fill=BOTH, padx=5, pady=5)
		# Text area for the sample packet
		text_frame = Frame(middle_frame)
		text_frame.pack(side=LEFT, expand=YES, fill=BOTH, padx=5)
		text_area = Text(text_frame, height=10, width=50, font=('Courier', 11, 'normal'))
		sbar = Scrollbar(text_frame)
		sbar.config(command=text_area.yview)
		text_area.config(yscrollcommand=sbar.set)
		sbar.pack(side=RIGHT, fill=Y)
		text_area.pack(side=LEFT, expand=YES, fill=BOTH)
		self.text = text_area
		self.text.config(state=DISABLED)
		self.text.tag_config('DEFINED', foreground='red')	# show text tagged with 'DEFINED' in red
		self.text.tag_config('HIGHLIGHTED', background='gray')
		self.text.tag_config('DELIM_FIELD', background='green')
		self.text.tag_config('DELIM_SUBFIELD', background='yellow')
		self.text.bind('<Button-3>', self.clear_highlights)
		# Format buttons
		Label(middle_frame, text='Show in:', font=('Sans', 9, 'bold')).pack(anchor=NW, padx=2)
		self.hex_btn = Button(middle_frame, text='HEX', width=4, bg='gray80', command=self.convert_to_hex)
		self.hex_btn.pack(anchor=NE, padx=5, pady=5)
		self.bin_btn = Button(middle_frame, text='BIN', width=4, bg='gray80', command=self.convert_to_bin)
		self.bin_btn.pack(anchor=NE, padx=5)
		self.ascii_btn = Button(middle_frame, text='ASCII', width=4, bg='gray80', command=self.convert_to_ascii)
		self.ascii_btn.pack(anchor=NE, padx=5, pady=5)

		# Text area for the protocol tree
		middle_frame2 = Frame(self)
		middle_frame2.pack(side=TOP, expand=YES, fill=BOTH, padx=5, pady=5)
		tree_frame = Frame(middle_frame2)
		tree_frame.pack(side=LEFT, expand=YES, fill=BOTH, padx=5)
		tree_area = Text(tree_frame, height=10, width=50, font=('Courier', 11, 'normal')) #width=71
		sbar2 = Scrollbar(tree_frame)
		sbar2.config(command=tree_area.yview)
		tree_area.config(yscrollcommand=sbar2.set)
		sbar2.pack(side=RIGHT, fill=Y)
		tree_area.pack(side=LEFT, expand=YES, fill=BOTH)
		self.tree = tree_area
		self.tree.tag_config('HIGHLIGHTED', background='gray')
		self.tree.tag_config('BOLD', font=('Courier', 11, 'bold'))
		self.tree.tag_bind(SEL, '<Button-1>', self.highlight_field)
		self.tree.bind('<Button-3>', self.clear_highlights)
		self.tree.config(state=DISABLED)
		ghost_frame = Frame(middle_frame2)		# Used just for getting the text areas' borders better in line.
		ghost_frame.pack(anchor=E, padx=28)		# originally set to 34 for Ubuntu
		
		# Define protocol buttons' frame contents
		proto_btn_frame = Frame(self)
		proto_btn_frame.pack(anchor=N, expand=YES, fill=X, padx=5, pady=5)
		Label(proto_btn_frame, text='Define protocol information:', font=('Sans', 9, 'bold')).pack(anchor=NW, padx=5)
		Button(proto_btn_frame, text='Define protocol', width=14, bg='gray80', command=self.define_protocol_info).pack(side=LEFT, padx=5, pady=5)
		Button(proto_btn_frame, text='Clear protocol tree', width=14, bg='gray80', command=self.clear_protocol_info).pack(side=LEFT, pady=5)
		
		# Define field buttons' frames' contents
		field_btn_frame = Frame(self)
		field_btn_frame.pack(anchor=S, expand=YES, fill=X, padx=5, pady=5)
		Label(field_btn_frame, text='Define field information:', font=('Sans', 9, 'bold')).pack(anchor=NW, padx=5)
		radio_btn_frame = Frame(field_btn_frame)
		radio_btn_frame.pack(anchor=NW)
		delimiter_btn_frame = Frame(field_btn_frame)
		delimiter_btn_frame.pack(anchor=NW)
		self.delimit_type = StringVar()
		self.radioFixed = Radiobutton(radio_btn_frame, text='Use fixed fields', width=13, anchor=W, variable=self.delimit_type, value='FIXED', command=self.check_field_delimit)
		self.radioFixed.select()
		self.radioFixed.pack(side=LEFT, padx=5)
		self.radioDelim = Radiobutton(radio_btn_frame, text='Use delimiters', width=13, anchor=W, variable=self.delimit_type, value='DELIMITERS', command=self.check_field_delimit)
		self.radioDelim.pack(side=LEFT)
		self.delimiters_btn = Button(delimiter_btn_frame, text='Define delimiters', width=14, bg='gray80', state=DISABLED, command=self.define_delimiters)
		self.delimiters_btn.pack(side=LEFT, padx=5)
		self.previous_field_btn = Button(delimiter_btn_frame, text='<--', width=2, bg='gray80', state=DISABLED, command=self.previous_delim_field)
		self.previous_field_btn.pack(side=LEFT)
		self.previous_subfield_btn = Button(delimiter_btn_frame, text='<', width=2, bg='gray80', state=DISABLED, command=self.previous_delim_subfield)
		self.previous_subfield_btn.pack(side=LEFT)
		self.next_subfield_btn = Button(delimiter_btn_frame, text='>', width=2, bg='gray80', state=DISABLED, command=self.next_delim_subfield)
		self.next_subfield_btn.pack(side=LEFT)
		self.next_field_btn = Button(delimiter_btn_frame, text='-->', width=2, bg='gray80', state=DISABLED, command=self.next_delim_field)
		self.next_field_btn.pack(side=LEFT)
		self.clear_delimiters_btn = Button(delimiter_btn_frame, text='Clear delimiters', width=14, bg='gray80', state=DISABLED, command=self.clear_delimiters)
		self.clear_delimiters_btn.pack(side=LEFT, padx=5)
		self.integer_btn = Button(field_btn_frame, text='Integer type field', width=14, bg='gray80', command=self.define_integer_type_field)
		self.integer_btn.pack(side=LEFT, padx=5, pady=5)
		self.other_btn = Button(field_btn_frame, text='Other type field', width=14, bg='gray80', command=self.define_other_type_field)
		self.other_btn.pack(side=LEFT, padx=10, pady=5)
		self.clear_field_btn = Button(field_btn_frame, text='Clear defined field', width=14, bg='gray80', command=self.clear_field)
		self.clear_field_btn.pack(side=LEFT, padx=5, pady=5)
		Button(field_btn_frame, text='Create dissector', width=14, bg='gray80', command=self.on_create).pack(side=RIGHT, padx=5, pady=5)
		
	def check_field_delimit(self):
		if self.delimit_type.get() == 'FIXED':
			self.delimiters_btn.config(state=DISABLED)
			self.previous_field_btn.config(state=DISABLED)
			self.next_field_btn.config(state=DISABLED)
			self.clear_delimiters_btn.config(state=DISABLED)
			self.integer_btn.config(state=NORMAL)
			self.other_btn.config(state=NORMAL)
			self.clear_field_btn.config(state=DISABLED)

		elif self.delimit_type.get() == 'DELIMITERS':
			self.delimiters_btn.config(state=NORMAL)
			self.integer_btn.config(state=DISABLED)
			self.other_btn.config(state=DISABLED)
			self.clear_field_btn.config(state=DISABLED)

####################################
#   Methods for the menu buttons   #
####################################

	def on_open(self):
		"""Pops up a file dialog for opening a file that
		contains a sample packet of the protocol to be defined."""
		filename = askopenfilename(filetypes=[('All files', '.*'), ('Text files', '.txt')])
		if filename:
			# Clear both text frame contents.
			self.text.config(state=NORMAL)
			self.tree.config(state=NORMAL)
			self.text.delete('1.0', END)
			self.tree.delete('1.0', END)
			self.text.config(state=DISABLED)
			self.tree.config(state=DISABLED)
			self.__init__()
			Info.init()
			format, content = check_file(filename)
			if format == 0:
				showerror('Error message', content)
				return
			elif format == 1:
				print 'File content is HEX.'
				self.show_in = 'HEX'
				self.set_text(text=content)
			elif format == 2:
				print 'File content is BIN.'
				self.show_in = 'BIN'
				self.set_text(text=content)
			elif format == 3:
				print 'File content is ASCII.'
				self.show_in = 'ASCII'
				# Save the unformatted ASCII content
				self.orig_ascii = content
				# Replace ASCII control characters with dots before printing
				for c in content:
					if re.match('[\x00-\x1F]|[\x7F]', c):
						content = content.replace(c, '.')

				self.set_text(text=content)

	def on_save_tree(self):
		"""Saves the protocol tree to a file."""
		proto = Info.get_proto_name()
		if len(proto) > 0:
			filename = proto.lower().replace(' ', '_')
		else:
			filename = 'proto_tree'

		filepath = asksaveasfilename(filetypes=[('Text files', '.txt'), ('All files', '.*')],
									 initialfile=filename, title='Save the protocol tree to a file')
		if filepath:
			try:
				f = open(filepath, 'w')
				tree = self.get_tree_structure()
				f.write('\n'.join(tree))
			except:
				showerror('Error message', 'Protocol tree could not be written to the file!')
			finally:
				f.close()
			
	def on_help(self):
		"""Show the help for using LuDis."""
		win = Toplevel(self)
		HelpWin(win, text_file='help.txt')

####################################################
#   Methods specific for the sample packet frame   #
####################################################

	def set_text(self, text='', file=None):
		"""Sets the content of the text area."""
		self.text.config(state=NORMAL)			# enable text area
		if file:
			text = open(file, 'r').read()
		self.text.delete('1.0', END)			# delete current text
		self.text.insert('1.0', text)			# add at line 1, col 0
		self.text.mark_set(INSERT, '1.0')		# set insert cursor
		self.text.config(state=DISABLED)		# disable text area
		
	def get_text(self):
		"""Returns the whole content of the text area."""
		return self.text.get('1.0', END+'-1c')
		
	def update_defined_fields(self):
		"""Updates the text in the packet frame content
		marked as DEFINED (colored in red)."""
		self.text.tag_remove('DEFINED', '1.0', END)
		for area in self.defined_table[self.show_in]:
			self.text.tag_add('DEFINED', area[0], area[1])
		if len(self.defined_table[self.show_in]) > 0:
			self.clear_field_btn.config(state=NORMAL)
		else:
			self.clear_field_btn.config(state=DISABLED)

####################################################
#   Methods specific for the protocol tree frame   #
####################################################

	def update_tree(self):
		"""Updates the protocol tree according to the
		information set in the Info class."""
		self.tree.config(state=NORMAL)
		self.tree.delete('1.0', END)
		self.tree.insert('1.0', Info.get_proto_name(), 'BOLD')
		if len(Info.get_proto_desc()) > 0:
			self.tree.insert(INSERT, ' (' + Info.get_proto_desc() + ')', 'BOLD')

		for field in Info.proto_fields:
			self.tree.insert(INSERT, '\n    ' + field.get_abbr() + ': ', 'BOLD')
			if field.get_value():
				self.tree.insert(INSERT, field.get_value())
			else:
				self.tree.insert(INSERT, '<value>')
			for subfield in field.subfields:
				self.tree.insert(INSERT, '\n        ' + subfield.get_abbr() + ': ', 'BOLD')
				if subfield.get_value():
					self.tree.insert(INSERT, subfield.get_value())
				else:
					self.tree.insert(INSERT, '<value>')
		
		self.tree.config(state=DISABLED)

		if len(Info.proto_name) > 0:
			self.save_btn.config(state=NORMAL)
		else:
			self.save_btn.config(state=DISABLED)

	def add_to_tree(self, text, line, indent=0):
		"""Adds a field to the protocol tree.

		text - The field to be added.
		line - The line to which the field is added.
		indent - Indentation level for the field.
		"""
		tree = self.get_tree_structure()
		if line > 0:
			line -= 1
		tree.insert(line, indent * '    ' + text)
		self.set_tree_structure(tree)

	def get_tree_structure(self):
		"""Returns the whole content of the protocol tree area."""
		tree_str = self.tree.get('1.0', END+'-1c')
		tree = tree_str.split('\n') 
		return tree

############################################################################
#   Method for creating the field/subfield lists according to delimiters   #
############################################################################

	def create_delim_field_list(self):
		"""Creates a list of the fields and subfields separated by delimiters."""
		packet = self.get_text()
		f_delim_indices = []
		delim = Info.field_delimiter.upper()
		delim_len = len(Info.field_delimiter.split())

		# Check that the sample packet contains field delimiters.
		if packet.find(delim) > 0:
			index = -1
			for i in range(0, packet.count(delim)):
				index = packet.find(delim, index + 1)			# index + delim_len changed to index + 1
				if index > -1:
					if Info.header_delimiter is not None and (index / 3 + delim_len - 1) < Info.header_delimiter[1]:
						f_delim_indices.append([index / 3 + delim_len - 1])		# Store the delimiter index as byte index
					elif Info.header_delimiter is None:
						if Info.header_length is not None and (index / 3 + delim_len - 1) < Info.header_length:
							f_delim_indices.append([index / 3 + delim_len - 1])		# Store the delimiter index as byte index
						elif Info.header_length_from_last_field is True:
							f_delim_indices.append([index / 3 + delim_len - 1])		# Store the delimiter index as byte index

			j = 0
			for i in range(0, len(f_delim_indices)):
				f_delim_indices[i].insert(0, j)			# Add beginning indices of the fields
				j = f_delim_indices[i][1] + 1

			# Convert the byte indices first to nibble indices, and then to SEL indices.
			for i in range(0, len(f_delim_indices)):
				start, end = nibbles_to_sel(f_delim_indices[i][0] * 2, f_delim_indices[i][1] * 2 + 1, 'HEX')
				self.field_borders.append([start, end])

			# Create tables for checking which fields and subfields are defined and which are not.
			Info.defined_delim_fields = [False] * len(self.field_borders)
			Info.defined_delim_subfields = [[]] * len(self.field_borders)

			# Highlight the first field in the list
			self.text.tag_add('DELIM_FIELD', self.field_borders[self.delim_field_num][0], self.field_borders[self.delim_field_num][1])
			# Enable other delimiter buttons
			self.clear_delimiters_btn.config(state=NORMAL)
			if packet.count(delim) > 1:
				self.next_field_btn.config(state=NORMAL)
				self.previous_field_btn.config(state=NORMAL)
		else:
			showerror('Error message', 'Defined field delimiter was not found in the sample packet!')
			return

		# Check if the fields of the sample packet contain subfield delimiters.
		subf_delim_indices = []
		subf_delim = Info.subfield_delimiter.upper()
		subf_delim_len = len(Info.subfield_delimiter.split())
		field_num = 0
		for field_border_bytes in f_delim_indices:
			field = ' '.join(packet.split()[field_border_bytes[0]:field_border_bytes[1] + 1])	# Inspect one field at a time
			subf_delim_indices.append([])	# Create a subfield list even if the field doesn't have any
			if field.find(subf_delim) > 0:
				index = -1
				for i in range(0, field.count(subf_delim)):
					index = field.find(subf_delim, index + 1) 		# index + subf_delim_len changed to index + 1
					if index > -1:
						# Store the delimiter index as byte index. The subfield delimiter is not included!
						subf_delim_indices[field_num].append([index / 3 + field_border_bytes[0] - 1])

				j = field_border_bytes[0]
				for i in range(0, len(subf_delim_indices[field_num])):
					subf_delim_indices[field_num][i].insert(0, j)					# Add beginning indices of the fields
					j = subf_delim_indices[field_num][i][1] + subf_delim_len + 1 	# Leave out the subfield delimiters

				# Add the last subfield that ends to the field delimiter.
				last_start = subf_delim_indices[field_num][len(subf_delim_indices[field_num]) - 1][1] + subf_delim_len + 1 	# Skip delimiter
				last_end = field_border_bytes[1] - (delim_len - 1) - 1 			# Leave out the field delimiter in the end
				# Check that there is bytes left from the field for the last subfield
				if last_start <= last_end:
					subf_delim_indices[field_num].append([last_start, last_end])
			
			field_num += 1

		# Convert the byte indices first to nibble indices, and then to SEL indices.
		for i in range(0, len(subf_delim_indices)):
			self.subfield_borders.append([])
			for j in range(0, len(subf_delim_indices[i])):
				start, end = nibbles_to_sel(subf_delim_indices[i][j][0] * 2, subf_delim_indices[i][j][1] * 2 + 1, 'HEX')
				self.subfield_borders[i].append([start, end])

		# Add an entry for each subfield in the defined subfields table.
		for i in range(0, len(self.subfield_borders)):
			Info.defined_delim_subfields[i] = [False] * len(self.subfield_borders[i])

		if len(self.subfield_borders[0]) > 0:
			self.next_subfield_btn.config(state=NORMAL)
			self.previous_subfield_btn.config(state=NORMAL)
			# Enable the field arrow buttons in case they are disabled.
			# Otherwise a field can't be selected after a subfield arrow button is
			# pressed when there is only one field.
			self.next_field_btn.config(state=NORMAL)
			self.previous_field_btn.config(state=NORMAL)

		self.use_delimiters = True
		self.radioFixed.config(state=DISABLED)
		self.radioDelim.config(state=NORMAL)
		self.bin_btn.config(state=DISABLED)
		self.ascii_btn.config(state=DISABLED)
		self.integer_btn.config(state=NORMAL)
		self.other_btn.config(state=NORMAL)

###############################################################################
#   Methods for choosing next/previous field/subfield in the delimiter list   #
###############################################################################

	def next_delim_field(self):
		"""Highlight the next field in the list limited by field delimiters."""
		self.delim_field_num += 1
		self.delim_subfield_num = -1
		if self.delim_field_num > len(self.field_borders) - 1:
			self.delim_field_num = 0
		self.text.tag_remove('DELIM_FIELD', '1.0', END)
		self.text.tag_remove('DELIM_SUBFIELD', '1.0', END)
		self.text.tag_add('DELIM_FIELD', self.field_borders[self.delim_field_num][0], self.field_borders[self.delim_field_num][1])
		# Enable buttons for browsing subfields, if the field contains any.
		try:
			if len(self.subfield_borders[self.delim_field_num]) > 0:
				self.next_subfield_btn.config(state=NORMAL)
				self.previous_subfield_btn.config(state=NORMAL)
			else:
				self.next_subfield_btn.config(state=DISABLED)
				self.previous_subfield_btn.config(state=DISABLED)
		except:
			self.next_subfield_btn.config(state=DISABLED)
			self.previous_subfield_btn.config(state=DISABLED)

	def previous_delim_field(self):
		"""Highlight the previous field in the list limited by field delimiters."""
		self.delim_field_num -= 1
		self.delim_subfield_num = -1
		if self.delim_field_num < 0:
			self.delim_field_num = len(self.field_borders) - 1
		self.text.tag_remove('DELIM_FIELD', '1.0', END)
		self.text.tag_remove('DELIM_SUBFIELD', '1.0', END)
		self.text.tag_add('DELIM_FIELD', self.field_borders[self.delim_field_num][0], self.field_borders[self.delim_field_num][1])
		# Enable buttons for browsing subfields, if the field contains any.
		try:
			if len(self.subfield_borders[self.delim_field_num]) > 0:
				self.next_subfield_btn.config(state=NORMAL)
				self.previous_subfield_btn.config(state=NORMAL)
			else:
				self.next_subfield_btn.config(state=DISABLED)
				self.previous_subfield_btn.config(state=DISABLED)
		except:
			self.next_subfield_btn.config(state=DISABLED)
			self.previous_subfield_btn.config(state=DISABLED)

	def next_delim_subfield(self):
		"""Highlight the next subfield in the list limited by subfield delimiters."""
		self.delim_subfield_num += 1
		if self.delim_subfield_num > len(self.subfield_borders[self.delim_field_num]) - 1:
			self.delim_subfield_num = 0
		self.text.tag_remove('DELIM_SUBFIELD', '1.0', END)
		self.text.tag_add('DELIM_SUBFIELD', self.subfield_borders[self.delim_field_num][self.delim_subfield_num][0],
										 self.subfield_borders[self.delim_field_num][self.delim_subfield_num][1])

	def previous_delim_subfield(self):
		"""Highlight the previous subfield in the list limited by subfield delimiters."""
		self.delim_subfield_num -= 1
		if self.delim_subfield_num < 0:
			self.delim_subfield_num = len(self.subfield_borders[self.delim_field_num]) - 1
		self.text.tag_remove('DELIM_SUBFIELD', '1.0', END)
		self.text.tag_add('DELIM_SUBFIELD', self.subfield_borders[self.delim_field_num][self.delim_subfield_num][0],
										 self.subfield_borders[self.delim_field_num][self.delim_subfield_num][1])

#######################################################
#   Methods for converting the sample packet format   #
#######################################################

	def convert_to_hex(self):
		"""Converts the text area content to hexadecimal."""
		if len(self.get_text()) < 2:
			showinfo('Info message', 'Open a sample packet first.')
			return
		# Clear highlights from both text frames.
		self.clear_highlights()

		# Check if content is already hexadecimal:
		if self.show_in == 'HEX':
			showinfo('Info message', 'Content is already hexadecimals.')
			return
		elif self.show_in == 'ASCII':
			if self.orig_ascii != '':
				data = self.orig_ascii		# read the original ASCII data
			elif self.text_content != '':
				data = self.text_content	# read from backup memory
		else:
			data = self.get_text()
			data = data.replace(' ', '')	# remove spaces

		hex_str = ''
		# Check if text is binary:
		if self.show_in == 'BIN' and re.match('[0-1]+$', data):
			hex_str = hex(int(data, 2))[2:]
			# Remove trailing 'L' if necessary.
			if hex_str[-1:] == 'L':
				hex_str = hex_str[:-1]
			# Add a beginning zero, if length not even.
			if len(hex_str) % 2 != 0:
				hex_str = '0' + hex_str
		# Check if text is ASCII:
		elif self.show_in == 'ASCII':
			# In this case the 'data' contains HEX that was backed up before transforming to ASCII
			if re.match('[0-9A-Fa-f]+$', data) and self.text_content != '':
				hex_str = data
			elif re.match('[\x00-\x7F]+$', data):
				hex_str = binascii.hexlify(data)
		else:
			showerror('Error message', 'Content must first be ASCII or binary!')
			return
		
		# Convert to hexadecimals:
		if hex_str != '':
			hex_str = hex_str.upper()
			hex_chopped = ''
			for start in range(0, len(hex_str), 2):
				if start + 2 <= len(hex_str):
					hex_chopped += hex_str[start:start+2] + ' '
				else:
					hex_chopped += hex_str[start:]		# add the remainings
					
			hex_chopped = hex_chopped.rstrip()		# remove possible whitespace at the end
			self.show_in = 'HEX'
			self.text_content = ''
			self.set_text(text=hex_chopped)
			# Mark all defined areas.
			self.update_defined_fields()
	
	def convert_to_bin(self):
		"""Converts the text area content to binary."""
		if len(self.get_text()) < 2:
			showinfo('Info message', 'Open a sample packet first.')
			return
		# Clear highlights from both text frames.
		self.clear_highlights()
		in_hex = False

		# Check if content is already binary:
		if self.show_in == 'BIN':
			showinfo('Info message', 'Content is already binary.')
			return	
		elif self.show_in == 'ASCII':
			if self.orig_ascii != '':
				data = self.orig_ascii		# read the original ASCII data
			elif self.text_content != '':
				data = self.text_content	# text_content is hexadecimal data without spaces
				in_hex = True
		else:
			data = self.get_text()
			data = data.replace(' ', '')	# remove spaces

		bin_str = ''
		# Check if text is hexadecimal:
		if self.show_in == 'HEX' and re.match('[0-9A-Fa-f]+$', data):
			bin_str = bin(int(data, 16))[2:]
		# Check if text is ASCII:
		elif self.show_in == 'ASCII' and re.match('[\x00-\x7F]+$', data):
			if in_hex:
				bin_str = bin(int(data, 16))[2:]
			else:
				hex_str = binascii.hexlify(data)
				bin_str = bin(int(hex_str, 16))[2:]
		else:
			showerror('Error message', 'Content must first be ASCII or hexadecimal!')
			return
			
		# Convert to binary:
		if bin_str != '':
			while len(bin_str) % 8 != 0:
				bin_str = '0' + bin_str
			bin_chopped = ''
			for start in range(0, len(bin_str), 8):
				if start + 8 <= len(bin_str):
					bin_chopped += bin_str[start:start+8] + ' '
				else:
					bin_chopped += bin_str[start:]		# add the remainings
					
			bin_chopped = bin_chopped.rstrip()		# remove possible whitespace at the end
			self.show_in = 'BIN'
			self.text_content = ''
			self.set_text(text=bin_chopped)
			# Mark all defined areas.
			self.update_defined_fields()
		
	def convert_to_ascii(self):
		"""Converts the text area content to ASCII."""
		if len(self.get_text()) < 2:
			showinfo('Info message', 'Open a sample packet first.')
			return
		# Clear highlights from both text frames.
		self.clear_highlights()

		# Check if content is already ASCII:
		if self.show_in == 'ASCII':
			showinfo('Info message', 'Content is already ASCII.')
			return
		data = self.get_text()
		data = ''.join(data.split())	# remove whitespaces
		ascii_hex = ''
		# Check if text is binary:
		if self.show_in == 'BIN' and re.match('[0-1]+$', data):
			ascii_hex = hex(int(data, 2))[2:]
			# Remove trailing 'L' if necessary.
			if ascii_hex[-1:] == 'L':
				ascii_hex = ascii_hex[:-1]
			# Add a beginning zero, if length not even.
			if len(ascii_hex) % 2 != 0:
				ascii_hex = '0' + ascii_hex
		# Check if text is hexadecimal:
		elif self.show_in == 'HEX' and re.match('[0-9A-Fa-f]+$', data):
			ascii_hex = data
		else:
			showerror('Error message', 'Content must first be hexadecimal or binary!')
			return
			
		# Convert to ASCII characters:
		if ascii_hex != '':
			ascii_chars = ''
			for i in range(0, len(ascii_hex), 2):
				ascii_dec = int(ascii_hex[i:i+2], 16)
				if (ascii_dec >= 32 and ascii_dec <= 126):
					ascii_chars += chr(ascii_dec)
				else:
					ascii_chars += '.'
			self.show_in = 'ASCII'
			self.text_content = ascii_hex	# backup unformatted content
			self.set_text(text=ascii_chars)
			# Mark all defined areas.
			self.update_defined_fields()
			
################################################
#   Methods for highlighting selected fields   #
################################################

	def choose_field_from_tree(self):
		"""Chooses a field from the protocol tree according to selection."""
		try:
			text = self.tree.get(SEL_FIRST, SEL_LAST)
			if text.isspace() == True:
				showerror('Error message', 'Please highlight a valid field instead of whitespaces!')
				return None
		except:
			return 'except'

		line_num1, line_num2 = self.tree.tag_ranges(SEL)
		line_num1 = int(str(line_num1).split('.')[0], 10)
		line_num2 = int(str(line_num2).split('.')[0], 10)
		if line_num1 != line_num2:
			showerror('Error message', 'Please highlight only one field/line!')
			return None

		return line_num1

	def highlight_field(self, event):
		"""Highlights the selected field."""
		line_num1 = self.choose_field_from_tree()
		if not line_num1:
			return
		elif line_num1 == 'except':
			showerror('Error message', 'Failed to read the highlighted field!')
			return

		s = self.tree.get(str(line_num1) + '.0', str(line_num1) + '.end')
		spaces_left = len(s) - len(s.lstrip())
		spaces_right = len(s) - len(s.rstrip())
		self.tree.tag_add('HIGHLIGHTED', str(line_num1) + '.' + str(spaces_left), str(line_num1) + '.end-' + str(spaces_right) + 'chars')
	
		# Highlight the corresponding data in the sample packet.
		start_ind = None
		end_ind = None
		if line_num1 == 1:
			start_ind = '1.0'
			end_ind = '1.end'
		else:
			num = 1
			for field in Info.proto_fields:
				num += 1
				if num == line_num1:
					start_byte = field.get_start()
					end_byte = field.get_end()
				for subfield in field.subfields:
					num += 1
					if num == line_num1:
						start_byte = subfield.get_start()
						end_byte = subfield.get_end()	

			start_nibble = 2 * start_byte
			end_nibble = 2 * end_byte + 1
			start_ind, end_ind = nibbles_to_sel(start_nibble, end_nibble, self.show_in)

		self.text.tag_add('HIGHLIGHTED', start_ind, end_ind)

	def clear_highlights(self, event=None):
		"""Clears all highlights from the packet frame."""
		self.text.tag_remove('HIGHLIGHTED', '1.0', END)
		self.tree.tag_remove('HIGHLIGHTED', '1.0', END)

##############################################################
#   Methods for defining/clearing the protocol information   #
##############################################################

	def define_protocol_info(self):
		"""Creates the protocol definition window."""
		if len(self.get_text()) == 0:
			showinfo('Info message', 'Open a sample packet first.')
			return
		win = Toplevel(self)
		ProtocolInfoWin(win)
	
	def clear_protocol_info(self):
		"""Clears the whole protocol definition and tree after confirmation."""
		if len(Info.get_proto_name()) == 0:
			showinfo('Info message', 'You haven\'t defined the protocol nor any protocol fields yet.')
			return
		if askyesno('Confirm', 'Are you sure you want to delete the whole protocol tree?'):
			self.clear_protocol_info_helper()	# Call the helper function
			return

	def clear_protocol_info_helper(self):
		"""Clears the whole protocol definition and tree without confirmation."""
		# Update the table containing areas that are tagged with 'DEFINED'.
		for format in ['BIN', 'HEX', 'ASCII']:
			del self.defined_table[format][:]
		self.update_defined_fields()

		temp_field_delim = Info.field_delimiter
		temp_subfield_delim = Info.subfield_delimiter
		Info.init()
		Info.field_delimiter = temp_field_delim
		Info.subfield_delimiter = temp_subfield_delim

		self.clear_highlights()
		self.update_tree()
		self.save_btn.config(state=DISABLED)
		return

######################################################
#   Methods for clearing field(s) and delimiter(s)   #
######################################################
			
	def clear_field(self):
		"""Clears the selected field definition."""
		line = self.choose_field_from_tree()
		# If the chosen field could not be read with SEL tag, try HIGHLIGHTED tag.
		if not line:
			return
		elif line == 'except':
			chosen = self.tree.tag_ranges('HIGHLIGHTED')
			if len(chosen) == 2:
				line = int(str(chosen[0]).split('.')[0], 10)
			else:
				showerror('Error message', 'Failed to read the chosen field! Make sure you have chosen only one field to be deleted.')
				return

		if line == 1:
			if askyesno('Confirm', 'Are you sure you want to delete the whole protocol tree?'):
				# Update the table containing areas that are tagged with 'DEFINED'.
				for format in ['BIN', 'HEX', 'ASCII']:
					self.defined_table[format] = []
				self.update_defined_fields()
				Info.init()
				self.clear_highlights()
				self.update_tree()
				return
			else:
				return
		else:
			num = 1
			for field in Info.proto_fields:
				num += 1
				if num == line:
					if askyesno('Confirm', 'The chosen field and all of its subfields will be deleted from the protocol tree.\n\n' +
								'Are you sure you want to continue?'):
						# Update the table containing areas that are tagged with 'DEFINED'.
						for format in ['BIN', 'HEX', 'ASCII']:
							first, last = nibbles_to_sel(field.get_start() * 2, field.get_end() * 2 + 1, format)
							self.defined_table[format].remove((first, last))
							# Remove also the marking from the defined_delim_fields table.
							try:
								index = self.field_borders.index([first, last])
								Info.defined_delim_fields[index] = False
							except ValueError:
								pass
							# Delete also all subfields of the selected field.
							for subfield in field.subfields:
								first, last = nibbles_to_sel(subfield.get_start() * 2, subfield.get_end() * 2 + 1, format)
								self.defined_table[format].remove((first, last))
								# Remove also the markings from the defined_delim_subfields table.
								for tbl in self.subfield_borders:
									field_index = self.subfield_borders.index(tbl)
									try:
										subfield_index = tbl.index([first, last])
										Info.defined_delim_subfields[field_index][subfield_index] = False
										break
									except ValueError:
										pass
						self.update_defined_fields()
						Info.proto_fields.remove(field)
						self.clear_highlights()
						self.update_tree()
						return
					else:
						return
				for subfield in field.subfields:
					num += 1
					if num == line:
						if askyesno('Confirm', 'The chosen subfield will be deleted from the protocol tree.\n\n' +
									'Are you sure you want to continue?'):
							# Update the table containing areas that are tagged with 'DEFINED'.
							for format in ['BIN', 'HEX', 'ASCII']:
								first, last = nibbles_to_sel(subfield.get_start() * 2, subfield.get_end() * 2 + 1, format)
								self.defined_table[format].remove((first, last))
								# Remove also the markings from the defined_delim_subfields table.
								for tbl in self.subfield_borders:
									field_index = self.subfield_borders.index(tbl)
									try:
										subfield_index = tbl.index([first, last])
										Info.defined_delim_subfields[field_index][subfield_index] = False
										break
									except ValueError:
										pass
							self.update_defined_fields()
							field.subfields.remove(subfield)
							self.clear_highlights()
							self.update_tree()
							return
						else:
							return
	
	def clear_delimiters(self):
		"""Clear all the delimiters related variables."""

		if len(Info.proto_fields) > 0:
			if not askyesno('Confirm', 'Also the field definitions will be deleted. Are you sure you want to continue?'):
				return

		self.use_delimiters = False
		self.field_delimiter = ''
		self.subfield_delimiter = ''
		self.delim_field_num = 0
		self.delim_subfield_num = 0

		# Empty the delimiter lists
		del self.field_borders[:]
		del self.subfield_borders[:]

		# Clear the highlights from the packet frame
		self.text.tag_remove('DELIM_FIELD', '1.0', END)
		self.text.tag_remove('DELIM_SUBFIELD', '1.0', END)

		# Enable and disable relevant buttons
		self.bin_btn.config(state=NORMAL)
		self.ascii_btn.config(state=NORMAL)
		self.radioFixed.config(state=NORMAL)
		self.radioDelim.config(state=NORMAL)
		self.delimiters_btn.config(state=NORMAL)
		self.previous_field_btn.config(state=DISABLED)
		self.next_field_btn.config(state=DISABLED)
		self.previous_subfield_btn.config(state=DISABLED)
		self.next_subfield_btn.config(state=DISABLED)
		self.integer_btn.config(state=DISABLED)
		self.other_btn.config(state=DISABLED)
		self.clear_delimiters_btn.config(state=DISABLED)

		# Update the table containing areas that are tagged with 'DEFINED'.
		for format in ['BIN', 'HEX', 'ASCII']:
			del self.defined_table[format][:]
		self.update_defined_fields()
		Info.diss_id = None
		Info.diss_table = None
		Info.subdiss_field = {'bytes': None, 'bitmask': None, 'field_num': None, 'subfield_num': None}
		Info.proto_fields = []
		Info.field_delimiter = ''
		Info.subfield_delimiter = ''
		Info.defined_delim_fields = []
		Info.defined_delim_subfields = []
		self.clear_highlights()
		self.update_tree()

	def handle_selection(self):
		"""Handles the selection from the text area.
		
		Checks the highlighted text area, rounds the selection to
		full nibbles, and sets the new corresponding values for the
		variables that delimit the selection.
		"""
		try:
			self.text.get(SEL_FIRST, SEL_LAST)
		except TclError:
			showerror('Error message', 'Highlight part of the data to be defined!\nOnly full nibbles can be selected!')
			return False
			
		self.sel_first, self.sel_last = self.text.tag_ranges(SEL)
		if self.show_in == 'BIN':
			self.sel_first_nibble, self.sel_last_nibble = sel_from_bin(self.sel_first, self.sel_last, as_nibbles=True)
		elif self.show_in == 'HEX':
			self.sel_first_nibble, self.sel_last_nibble = sel_from_hex(self.sel_first, self.sel_last, as_nibbles=True)
		elif self.show_in == 'ASCII':
			first_byte, last_byte = sel_from_ascii(self.sel_first, self.sel_last)
			self.sel_first_nibble = 2 * first_byte
			self.sel_last_nibble = 2 * last_byte + 1
		
		if self.sel_first_nibble == None or self.sel_last_nibble == None:
			showerror('Error message', 'Highlight more data!\nOnly full nibbles can be selected!')
			return False
			
		# Change the selection area to correspond the full nibbles.
		new_sel_first, new_sel_last = nibbles_to_sel(self.sel_first_nibble, self.sel_last_nibble, self.show_in)
		if not new_sel_first or not new_sel_last:
			showerror('Error message', 'Conversion from nibbles to selection area failed!')
			return False

		self.sel_first, self.sel_last = new_sel_first, new_sel_last
		return True
		
	def check_field_boundaries(self):
		start, end = 0, 0
		if self.show_in == 'BIN':
			start, end = sel_from_bin(self.sel_first, self.sel_last)
		elif self.show_in == 'HEX':
			start, end = sel_from_hex(self.sel_first, self.sel_last)
		elif self.show_in == 'ASCII':
			start, end = sel_from_ascii(self.sel_first, self.sel_last)

		if Info.header_delimiter is not None and end < Info.header_delimiter[1]:
			return True
		elif Info.header_length is not None and end < Info.header_length:
			return True
		elif Info.header_length_from_last_field is True:
			return True
		else:
			return False

###############################################
#   Methods for creating the pop-up windows   #	
###############################################
	
	def define_delimiters(self):
		"""Creates a pop-up window for defining the delimiters for fields and subfields."""
		if len(Info.get_proto_name()) == 0:
			showinfo('Info message', 'You must first define the protocol information.')
			return
		if self.show_in != 'HEX':
			showinfo('Info message', 'Please switch to HEX mode before defining the delimiters.')
			return
		win = Toplevel(self)
		DelimitersWin(win)

	def define_integer_type_field(self):
		"""Creates a pop-up window for defining integer type data."""
		if len(Info.get_proto_name()) == 0:
			showinfo('Info message', 'You must first define the protocol information.')
			return
		if not self.use_delimiters:
			success = self.handle_selection()
			if not self.check_field_boundaries():
				showerror('Error message', 'Field boundaries exceed the header length!')
				return
		else:
			success = True

		if not success:
			return
		win = Toplevel(self)
		IntegerTypeWin(win)
		
	def define_other_type_field(self):
		"""Creates a pop-up window for defining other type data."""
		if len(Info.get_proto_name()) == 0:
			showinfo('Info message', 'You must first define the protocol information.')
			return
		if not self.use_delimiters:
			success = self.handle_selection()
			if not self.check_field_boundaries():
				showerror('Error message', 'Field boundaries exceed the header length!')
				return
		else:
			success = True

		if not success:
			return
		win = Toplevel(self)
		OtherTypeWin(win)
		
	def on_create(self):
		"""Creates a pop-up window for creating the protocol dissector."""
		if not Info.get_proto_name():
			showerror('Error message', 'You haven\'t defined a protocol yet!')
			return
		elif len(Info.proto_fields) == 0:
			showerror('Error message', 'You haven\'t defined any fields yet!')
			return

		# Check that the header and payload lengths are valid together.
		format = 0
		packet = ''
		if self.show_in == 'BIN':
			format = 1
			packet = self.get_text()
		elif self.show_in == 'HEX':
			format = 2
			packet = self.get_text()
		elif self.show_in == 'ASCII':
			if self.text_content != '':
				format = 2
				packet = self.text_content
			elif self.orig_ascii != '':
				format = 3
				packet = self.orig_ascii

		ret = Info.check_header_and_payload_lengths(packet, format)
		if ret == 0:
			pass
		elif ret == 1:
			showerror('Error message', 'Payload delimiter is not after the header!\n\n' + 
					  'Correct the header and payload length definitions, or delete header fields that overlap with the payload.')
			return
		elif ret == 2:
			showerror('Error message', 'Payload delimiter is not inside the sample packet!')
			return
		elif ret == 3:
			showerror('Error message', 'Header field that defines the payload length is not inside the header!\n\n' + 
					  'Make sure the byte indices are inside the header.')
			return
		elif ret == 4:
			showerror('Error message', 'Invalid header field number!\n\n' +
					  'The given field number is out of range. Check the number of defined header fields and note that' +
					  ' field indexing starts from 0.')
			return
		elif ret == 5:
			showerror('Error message', 'Invalid header subfield number!\n\n' +
					  'The given subfield number is out of range. Check the number of defined subfields of the specified' +
					  ' header field and note that subfield indexing starts from 0.')
			return
		elif ret == 6:
			showerror('Error message', 'The value of the specified header field/subfield is greater than the number of' +
					  ' bytes left after the header!\n\nMake sure there is at least as many bytes left after the header' +
					  ' as the payload length field/subfield indicates.')
			return
		elif ret == 7:
			showerror('Error message', 'Header fields exceed the given header length!\n\n' + 
					  'Correct the given header length or delete the header fields that exceed the specified length.')
			return
		elif ret == 8:
			showerror('Error message', 'Header fields exceed the header length defined by the header delimiter!\n\n' + 
					  'Change the header delimiter or delete the header fields that exceed the header length.')
			return

		win = Toplevel(self)
		CreateDissectorWin(win)


def main():
	"""The main function.

	Creates the main window and launches it.
	"""
	root = Tk()
	root.geometry('750x630+300+50')			# Set the size of the main window.
	root.resizable(FALSE, FALSE)
	try:
		LuDis(parent=root, file=sys.argv[1]).mainloop()	# Filename given on command line.
	except IndexError:
		LuDis(parent=root).mainloop()

if __name__ == "__main__":
	main()