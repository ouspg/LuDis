############################################
#   Module for storing all the protocol,   #
#   field, and subfield information.       #
#   Author: Jarmo Luomala (2013)           #
############################################

import string

class Info:

	# General protocol information variables
	proto_name = ''
	proto_desc = ''
	parent_diss_table = None
	diss_id = None
	diss_table = None
	diss_table_type = None
	diss_table_base = None
	subdiss_field = {'bytes': None, 'bitmask': None, 'field_num': None, 'subfield_num': None}
	proto_fields = []		# Table that contains all the defined fields (and subfields in them).

	# Field and subfield delimiter related variables
	field_delimiter = ''
	subfield_delimiter = ''
	defined_delim_fields = []
	defined_delim_subfields = []
	
	# Header and payload length variables
	header_length_from_last_field = False	# Header length - use end of the last header field
	header_length = None					# Header length - use given length (number of bytes)
	header_delimiter = None					# Header length - use delimiter
	payload_length_use_rest = False			# Payload length - use all bytes after the header
	payload_delimiter = None				# Payload length - use delimiter
	payload_length_field_num = None			# Payload length - use header field (field number)
	payload_length_subfield_num = None		# Payload length - use header field (subfield number)
	payload_length_bytes = None

	@classmethod
	def init(cls):
		"""Initialize/reset the Info class' variables."""
		cls.proto_name = ''
		cls.proto_desc = ''
		cls.parent_diss_table = None
		cls.diss_id = None
		cls.diss_table = None
		cls.diss_table_type = None
		cls.diss_table_base = None
		# cls.proto_subdiss_field = {'bytes': None, 'bitmask': None}
		cls.subdiss_field = {'bytes': None, 'bitmask': None, 'field_num': None, 'subfield_num': None}
		cls.proto_fields = []
		cls.field_delimiter = ''
		cls.subfield_delimiter = ''
		cls.defined_delim_fields = []
		cls.defined_delim_subfields = []
		cls.header_length_from_last_field = False
		cls.header_length = None
		cls.header_delimiter = None
		cls.payload_length_use_rest = False
		cls.payload_delimiter = None
		cls.payload_length_field_num = None
		cls.payload_length_subfield_num = None
		cls.payload_length_bytes = None
	
	@classmethod
	def clear_header_and_payload_length_data(cls):
		cls.header_length_from_last_field = False
		cls.header_length = None
		cls.header_delimiter = None
		cls.payload_length_use_rest = False
		cls.payload_delimiter = None
		cls.payload_length_field_num = None
		cls.payload_length_subfield_num = None
		cls.payload_length_bytes = None

	@classmethod
	def get_proto_name(cls):
		"""Get the protocol name."""
		return cls.proto_name
	
	@classmethod
	def set_proto_name(cls, name):
		"""Set the protocol name."""
		if len(name) == 0 or name.isspace():
			return False
		# Check that the given string is ASCII.
		try:
			name.decode('ascii')
		except UnicodeDecodeError:
			return False
		cls.proto_name = name
		return True
		
	@classmethod
	def get_proto_desc(cls):
		"""Get the protocol description."""
		return cls.proto_desc
	
	@classmethod
	def set_proto_desc(cls, desc):
		"""Set the protocol description."""
		if len(desc) == 0 or desc.isspace():
			return False
		# Check that the given string is ASCII.
		try:
			desc.decode('ascii')
		except UnicodeDecodeError:
			return False
		cls.proto_desc = desc
		return True
		
	@classmethod
	def get_parent_dissector_table(cls):
		"""Get the parent dissector table."""
		return cls.parent_diss_table

	@classmethod
	def set_parent_dissector_table(cls, table):
		"""Set the parent dissector table."""
		# No whitespaces allowed.
		if len(table) == 0 or table.isspace() or table.count(' ') != 0:
			return False
		# Table name should be given in lowercase.
		if not table.islower():
			return False
		# Check that the given string is ASCII.
		try:
			table.decode('ascii')
		except UnicodeDecodeError:
			return False
		cls.parent_diss_table = table.strip()
		return True

	@classmethod
	def get_dissector_id(cls):
		"""Get the protocol dissector ID.
		
		Dissector ID is used to access the dissector table of
		the parent dissector (ID ~ port number).
		"""
		return cls.diss_id
		
	@classmethod
	def set_dissector_id(cls, id):
		"""Get the protocol dissector ID.
		
		Dissector ID is used to access the dissector table of
		the parent dissector (ID ~ port number).
		"""
		# ID mustn't start with 0, if other numbers follow.
		if len(id) > 1 and id.startswith('0'):
			return False
		if not id.isdigit():
			return False
		cls.diss_id = id
		return True
		
	@classmethod
	def get_dissector_table(cls):
		"""Get the dissector table."""
		return cls.diss_table
	
	@classmethod
	def set_dissector_table(cls, table):
		"""Set the dissector table."""
		# No whitespaces allowed.
		if len(table) == 0 or table.isspace() or table.count(' ') != 0:
			return False
		# Table name should be given in lowercase.
		if not table.islower():
			return False
		# Check that the given string is ASCII.
		try:
			table.decode('ascii')
		except UnicodeDecodeError:
			return False
		cls.diss_table = table.strip()
		return True
		
	@classmethod
	def set_dissector_table_type(cls, diss_table_type):
		cls.diss_table_type = 'ftypes.' + diss_table_type
		return True

	@classmethod
	def set_dissector_table_base(cls, diss_table_base):
		cls.diss_table_base = 'base.' + diss_table_base
		return True

	@classmethod
	def get_subdiss_field_bytes(cls):
		"""Get the byte indices of the protocol's subdissector field."""
		return cls.subdiss_field['bytes']
		
	@classmethod
	def set_subdiss_field_bytes(cls, bytes):
		"""Set the byte indices of the protocol's subdissector field."""
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
				last_header_byte = None
				if cls.header_length is not None:
					last_header_byte = cls.header_length - 1
				else:
					last_field = cls.proto_fields[len(cls.proto_fields) - 1]
					last_header_byte = last_field.end

				subdiss_field_end = None
				if len(indices) == 2:
					subdiss_field_end = indices[1]
				else:
					subdiss_field_end = indices[0]

				if int(subdiss_field_end) <= last_header_byte:
					cls.subdiss_field['bytes'] = indices
					return True
				else:
					return False
		else:
			return False
		
	@classmethod
	def get_subdiss_field_bitmask(cls):
		"""Get the bitmask for the bytes of the protocol's subdissector field."""
		return cls.subdiss_field['bitmask']
		
	@classmethod
	def set_subdiss_field_bitmask(cls, bitmask):
		"""Set the bitmask for the bytes of the protocol's subdissector field.
		
		Bitmask must be given in hexadecimal, either in form 1) 0x0FFF
		or in form 2) 0FFF .
		"""
		if len(bitmask) == 0 or bitmask.isspace():
			return False
		bitmask = ''.join(bitmask.split())
		if bitmask.startswith('0x'):
			array = bitmask.split('0x')
			if len(array) != 2:
				return False
			bitmask = array[1]
		if len(bitmask) % 2 != 0:
			return False
		
		for char in bitmask:
			if char in string.hexdigits:
				pass
			else:
				return False
				
		cls.subdiss_field['bitmask'] = bitmask
		return True

	@classmethod
	def set_subdiss_id_field_num(cls, field_num):
		"""Set the field number/index of the field which contains the protocol's subdissector ID.

		The subdissector ID is used for addressing the payload of the parent dissector
		to the correct subdissector.
		"""
		if field_num.isdigit():
			if len(field_num) > 1 and field_num.startswith('0'):
				return False
			if int(field_num) >= 0 and int(field_num) < len(cls.proto_fields):
				cls.subdiss_field['field_num'] = int(field_num)
				return True

		return False

	@classmethod
	def set_subdiss_id_subfield_num(cls, subfield_num):
		"""Set the subfield number/index of the subfield which contains the protocol's subdissector ID.

		The subdissector ID is used for addressing the payload of the parent dissector
		to the correct subdissector.
		"""
		if subfield_num.isdigit():
			if len(subfield_num) > 1 and subfield_num.startswith('0'):
				return False			
			field_num = cls.subdiss_field['field_num']
			field = cls.proto_fields[field_num]

			if int(subfield_num) >= 0 and int(subfield_num) < len(field.subfields):
				cls.subdiss_field['subfield_num'] = int(subfield_num)
				return True

		return False

	@classmethod
	def add_field(cls, new_field):
		"""Add a new field to the protocol tree."""
		if not isinstance(new_field, Field):
			return False
		start = new_field.get_start()
		end = new_field.get_end()
		if start == None or end == None:
			return False
		previous = None
		for old_field in cls.proto_fields:
			old_index = cls.proto_fields.index(old_field)
			# The new field comes before an already defined field.
			if start < old_field.get_start() and end < old_field.get_start():
				if previous and (start <= previous.get_end()):
					return False
				cls.proto_fields.insert(old_index, new_field)
				return True
			# The new field is a subfield of another field.
			elif start >= old_field.get_start() and end <= old_field.get_end() \
			and not (start == old_field.get_start() and end == old_field.get_end()):
				return old_field.add_subfield(new_field)
			# The new field is added to the end of the list.
			elif old_index == len(cls.proto_fields) - 1:
				if start > old_field.get_end():
					cls.proto_fields.append(new_field)
					return True
			previous = old_field

		# In case the field list is empty.
		if len(cls.proto_fields) == 0:
			cls.proto_fields.append(new_field)
			return True

		return False

	@classmethod
	def check_header_and_payload_lengths(cls, packet, format):
		"""Check that the defined payload length is valid when the
		header length is determined by the last header field."""
		packet_length = 0
		# Binary
		if format == 1:
			packet_length = len(packet.replace(' ', '')) / 8
		# Hexadecimal
		elif format == 2:
			packet_length = len(packet.replace(' ', '')) / 2
		# ASCII
		elif format == 3:
			packet_length = len(packet)

		last_field = cls.proto_fields[len(cls.proto_fields) - 1]

		# 1) Header ends to the last header field.
		if cls.header_length_from_last_field:
			last_header_byte = last_field.end
		# 2) Header length is specified by the user.
		elif cls.header_length is not None:
			last_header_byte = cls.header_length - 1 	# Minus 1, because indices start from 0.
			# Inform the user if the header fields exceed the given header length.
			if last_header_byte < last_field.end:
				return 7
		# 3) Header length is defined by a delimiter.
		elif cls.header_delimiter is not None:
			last_header_byte = cls.header_delimiter[1] + (len(cls.header_delimiter[0].replace(' ', '')) / 2) - 1
			# Inform the user if the header fields exceed the header length defined by the delimiter.
			if cls.header_delimiter[1] <= last_field.end:
				return 8

		# 1) Payload contains all the bytes after the header.
		if cls.payload_length_use_rest:
			return 0
		# 2) Payload length is defined by a delimiter.
		elif cls.payload_delimiter is not None:
			if cls.payload_delimiter[1] > last_header_byte:
				delim_length = len(cls.payload_delimiter[0].replace(' ', '')) / 2
				# if cls.payload_delimiter[1] == packet_length - delim_length:
				# 	return 0
				if cls.payload_delimiter[1] + delim_length - 1 <= packet_length:
					return 0
				else:
					return 2
			else:
				return 1
		# 3) Payload length is defined by a specific header field/subfield.
		elif cls.payload_length_field_num is not None:
			if cls.payload_length_field_num <= len(cls.proto_fields) - 1:
				field = cls.proto_fields[cls.payload_length_field_num]
				start = None
				end = None
				# Payload length is defined by a subfield.
				if cls.payload_length_subfield_num is not None:
					if cls.payload_length_subfield_num <= len(field.subfields) - 1:
						subfield = field.subfields[cls.payload_length_subfield_num]
						start = subfield.get_start()
						end = subfield.get_end()
					else:
						return 5
				# Payload length is defined by a field.
				else:
					# In delimiter case, the field delimiter is included in field.
					start = field.get_start()
					field_delim_len = len(cls.field_delimiter.replace(' ', '')) / 2
					end = field.get_end() - field_delim_len

				payload_length = 0
				# Packet content is binary
				if format == 1:
					packet_str = packet.replace(' ', '')
					length_field = packet_str[(start * 8):(end * 8 + 8)]
					payload_length = int(length_field, 2)
					if payload_length <= packet_length - (last_header_byte + 1):
						return 0
					else:
						return 6
				# Packet content is hexadecimal
				elif format == 2:
					packet_str = packet.replace(' ', '')
					length_field = packet_str[(start * 2):(end * 2 + 2)]
					payload_length = int(length_field, 16)
					if payload_length <= packet_length - (last_header_byte + 1):
						return 0
					else:
						return 6
				# Packet content is ASCII
				elif format == 3:
					length_field = packet[start:end + 1]
					payload_length = binascii.hexlify(length_field)
					payload_length = int(payload_length, 16)
					if payload_length <= packet_length - (last_header_byte + 1):
						return 0
					else:
						return 6
			else:
				return 4


class Field(object):

	def __init__(self):
		self.type = None #''
		self.abbr = None #''
		self.name = None #''
		self.base = None #''
		self.desc = None #''
		self.valstr = None
		self.mask = None
		self.start = None		# as byte index (integer)
		self.end = None			# as byte index (integer)
		self.value = None
		self.subfields = []		# Table that contains all subfields of this field.

	def get_type(self):
		return self.type

	def set_type(self, field_type):
		self.type = field_type
		return True

	def get_abbr(self):
		return self.abbr

	def set_abbr(self, abbr):
		if len(abbr) == 0 or abbr.isspace() or abbr.find('.') >= 0:
			return False
		# Check that the given string is ASCII.
		try:
			abbr.decode('ascii')
		except UnicodeDecodeError:
			return False
		abbr = abbr.replace(' ', '_')
		self.abbr = abbr
		return True

	def get_name(self):
		return self.name

	def set_name(self, name):
		if len(name) == 0 or name.isspace():
			return False
		# Check that the given string is ASCII.
		try:
			name.decode('ascii')
		except UnicodeDecodeError:
			return False
		self.name = name
		return True

	def get_base(self):
		return self.base

	def set_base(self, base):
		if base == 'UNKNOWN':
			self.base = None
		else:
			self.base = 'base_' + base
		return True

	def get_desc(self):
		return self.desc

	def set_desc(self, desc):
		if len(desc) == 0 or desc.isspace():
			return False
		# Check that the given string is ASCII.
		try:
			desc.decode('ascii')
		except UnicodeDecodeError:
			return False
		self.desc = desc
		return True

	def get_valuestring(self):
		return self.valstr

	def set_valuestring(self, valstr):
		# Check that the given string is ASCII.
		try:
			valstr.decode('ascii')
		except UnicodeDecodeError:
			return False
		temp_dict = {}
		valstr_table = valstr.split(',')
		for val_tuple in valstr_table:
			key_val = val_tuple.split('=')
			if len(key_val) != 2:
				err_msg = 'Each key-value pair must be separated by "=" sign!'
				return (False, err_msg)
			key = key_val[0]
			val = key_val[1]
			key = key.strip()
			val = val.strip()
			# Check validity of the key.
			if key.startswith('[') and key.endswith(']'):
				try:
					key = int(key[1:-1], 10)
				except ValueError:
					err_msg = 'Keys must be presented as integers surrounded by square brackets!'
					return (False, err_msg)
			else:
				err_msg = 'Keys must be presented as integers surrounded by square brackets!'
				return (False, err_msg)
			
			# Check validity of the value.
			if (val.startswith("'") and val.endswith("'")) or (val.startswith('"') and val.endswith('"')):
				val = val[1:-1]
				if val.isspace():
					err_msg = 'Values cannot consist of whitespaces only!'
					return (False, err_msg)
				val = val.replace(' ', '_')
				for char in val:
					if char.isalnum():
						continue
					# Accept also underscores.
					elif ord(char) == 95:
						continue
					else:
						err_msg = 'Values can contain only alphabets, digits, and underscores!'
						return (False, err_msg)

				# Key-value pair is valid, store it to a temporary dictionary.
				temp_dict[key] = val
			else:
				err_msg = 'Values must be surrounded by either single or double quotation marks!'
				return (False, err_msg)

		# Every key-value pair is valid, copy the temporary dictionary to the field info.
		self.valstr = temp_dict.copy()
		return (True, None)

	def get_bitmask(self):
		return self.mask

	def set_bitmask(self, mask):
		mask = mask.replace(' ', '')
		if not mask.startswith('0x'):
			err_msg = 'Bitmask must start with "0x" prefix!'
			return (False, err_msg)
		if (len(mask) - 2) != (self.get_end() - self.get_start() + 1) * 2:
			err_msg = 'Bitmask must be as long as the field (in bytes)!'
			return (False, err_msg)
		for c in mask[2:]:
			if c not in string.hexdigits:
				err_msg = 'Bitmask must consist of valid hexadecimals!'
				return (False, err_msg)
		self.mask = mask
		return (True, None)

	def get_start(self):
		# Returns the start of the field as integer type.
		return self.start

	def set_start(self, start):
		# Sets the start of the field as integer type.
		self.start = start
		return True

	def get_end(self):
		# Returns the end of the field as integer type.
		return self.end

	def set_end(self, end):
		# Sets the end of the field as integer type.
		self.end = end
		return True

	def get_value(self):
		return self.value

	def get_length(self):
		if self.start is not None and self.end is not None:
			return self.end + 1 - self.start
		else:
			return 0

	def set_value(self, value, format):
		ascii_hex = ''
		if format == 'ASCII':
			self.value = value
			return True
		elif format == 'HEX':
			value = ''.join(value.split())
			ascii_hex = value
		elif format == 'BIN':
			value = ''.join(value.split())
			ascii_hex = hex(int(value, 2))[2:]
			# Remove trailing 'L' if necessary.
			if ascii_hex[-1:] == 'L':
				ascii_hex = ascii_hex[:-1]
			# Add a beginning zero, if length not even.
			if len(ascii_hex) % 2 != 0:
				ascii_hex = '0' + ascii_hex
		else:
			return False

		if ascii_hex != '':
			ascii_chars = ''
			for i in range(0, len(ascii_hex), 2):
				ascii_dec = int(ascii_hex[i:i+2], 16)
				if (ascii_dec >= 32 and ascii_dec <= 126):
					ascii_chars += chr(ascii_dec)
				elif ascii_dec == 7:
					ascii_chars += r'\a'
				elif ascii_dec == 8:
					ascii_chars += r'\b'
				elif ascii_dec == 9:
					ascii_chars += r'\t'
				elif ascii_dec == 10:
					ascii_chars += r'\n'
				elif ascii_dec == 11:
					ascii_chars += r'\v'
				elif ascii_dec == 12:
					ascii_chars += r'\f'
				elif ascii_dec == 13:
					ascii_chars += r'\r'
				else:
					ascii_chars += '.'
			self.value = ascii_chars
			return True

		return False

	def add_subfield(self, new_subf):
		start = new_subf.get_start()
		end = new_subf.get_end()
		previous = None
		for old_subf in self.subfields:
			old_index = self.subfields.index(old_subf)
			# The new subfield comes before an already defined subfield.
			if start < old_subf.get_start() and end < old_subf.get_start():
				if previous and (start <= previous.get_end()):
					return False
				self.subfields.insert(old_index, new_subf)
				return True
			# The new field is added to the end of the list.
			elif old_index == len(self.subfields) - 1:
				if start > old_subf.get_end():
					self.subfields.append(new_subf)
					return True
			previous = old_subf

		# In case the field list is empty.
		if len(self.subfields) == 0:
			self.subfields.append(new_subf)
			return True

		return False


if __name__ == '__main__':
	print '--- TEST: get_proto_name() ---'
	print 'Get before initialization:', Info.get_proto_name()
	print 'Set with invalid parameter:', Info.set_proto_name('  \n ')
	print 'Set with valid parameter:', Info.set_proto_name('http')
	print 'Get after initialization:', Info.get_proto_name()
	
	print '--- TEST: get_proto_desc() ---'
	print 'Get before initialization:', Info.get_proto_desc()
	print 'Set with invalid parameter:', Info.set_proto_desc('')
	print 'Set with valid parameter:', Info.set_proto_desc('Hypertext Transfer Protocol')
	print 'Get after initialization:', Info.get_proto_desc()
	
	print '--- TEST: get_dissector_id() ---'
	print 'Get before initialization:', Info.get_dissector_id()
	print 'Set with invalid parameter:', Info.set_dissector_id('0987654')
	print 'Set with valid parameter:', Info.set_dissector_id('87654')
	print 'Get after initialization:', Info.get_dissector_id()
	
	print '--- TEST: get_dissector_table() ---'
	print 'Get before initialization:', Info.get_dissector_table()
	print 'Set with invalid parameter:', Info.set_dissector_table('\n\n\t\n')
	print 'Set with valid parameter:', Info.set_dissector_table('tcp')
	print 'Get after initialization:', Info.get_dissector_table()
	
	print '--- TEST: get_subdiss_field_bytes() ---'
	print 'Get before initialization:', Info.get_subdiss_field_bytes()
	print 'Set with invalid parameter:', Info.set_subdiss_field_bytes('2--5')
	print 'Set with invalid parameter:', Info.set_subdiss_field_bytes('2-53-1')
	print 'Set with invalid parameter:', Info.set_subdiss_field_bytes('3-1')
	print 'Set with valid parameter:', Info.set_subdiss_field_bytes('8-12')
	print 'Get after initialization:', Info.get_subdiss_field_bytes()
	
	print '--- TEST: get_subdiss_field_bitmask() ---'
	print 'Get before initialization:', Info.get_subdiss_field_bitmask()
	print 'Set with invalid parameter:', Info.set_subdiss_field_bitmask('0x0xFF')
	print 'Set with invalid parameter:', Info.set_subdiss_field_bitmask('0xFER9')
	print 'Set with invalid parameter:', Info.set_subdiss_field_bitmask('0xABCDE')
	print 'Set with valid parameter:', Info.set_subdiss_field_bitmask('0x0FF0')
	print 'Set with valid parameter:', Info.set_subdiss_field_bitmask('0987654321ABCDEF')
	print 'Get after initialization:', Info.get_subdiss_field_bitmask()

	print '--- TEST: set_valuestring() ---'
	f1 = Field()
	print 'Get before initialization:', f1.get_valuestring()
	print 'Set with invalid parameter:', f1.set_valuestring('[2]=="Test"')
	print 'Set with invalid parameter:', f1.set_valuestring("[2e3] = 'Test'")
	print 'Set with invalid parameter:', f1.set_valuestring("[999] = 'Right', [1432] = Wrong")
	print 'Set with valid parameter:', f1.set_valuestring(" [100]  = 'Secret'")
	print 'Get after initialization:', f1.get_valuestring()
	print 'Set with valid parameter:', f1.set_valuestring('[0]="None", [1] = "Regular", [123]= "Get to da choppa"')
	print 'Get after initialization:', f1.get_valuestring()
	del f1

	print '--- TEST: set_bitmask() ---'
	f1 = Field()
	f1.set_start(0); f1.set_end(2)
	print 'Get before initialization:', f1.get_bitmask()
	print 'Set with invalid parameter:', f1.set_bitmask('FCAB38749')
	print 'Set with invalid parameter:', f1.set_bitmask('0xFA3CGE')
	print 'Set with invalid parameter:', f1.set_bitmask('0xFFFFFFF')
	print 'Set with valid parameter:', f1.set_bitmask('0xABCDEF')
	print 'Get after initialization:', f1.get_bitmask()
	print 'Set with valid parameter:', f1.set_bitmask('0xFF 00 AA')
	print 'Get after initialization:', f1.get_bitmask()
	del f1
	
	f1 = Field(); f2 = Field(); f3 = Field()
	f1.set_name('1st field'); f2.set_name('2nd field'); f3.set_name('3rd field')
	s1 = Field(); s2 = Field(); s3 = Field()
	s1.set_name('1st subfield'); s2.set_name('2nd subfield'); s3.set_name('3rd subfield')
	f1.set_start(0); f1.set_end(4); f2.set_start(4); f2.set_end(6); f3.set_start(9); f3.set_end(12)
	s1.set_start(0); s1.set_end(2); s2.set_start(2); s2.set_end(4); s3.set_start(10); s3.set_end(12)
	Info.add_field(f1); Info.add_field(f2); Info.add_field(f3)
	Info.add_field(s2); Info.add_field(s1); Info.add_field(s3)
	print '--- PROTO FIELDS ---'
	for item in Info.proto_fields:
		print item.get_name(), 'start:', item.get_start(), 'end:', item.get_end()
		for subitem in item.subfields:
			print '    ', subitem.get_name(), 'start:', subitem.get_start(), 'end:', subitem.get_end()