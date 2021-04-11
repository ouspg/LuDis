#####################################################
#   Module for generating the protocol dissectors.  #
#   Author: Jarmo Luomala (2013)                    #
#####################################################

import string
import os
import binascii

from info import Info, Field

# Reserved keywords in Lua, to avoid using them as variable names.
LUA_KEYWORDS = [
	'and', 'break', 'do', 'else', 'elseif', 'end', 'false', 'for',
	'function', 'if', 'in', 'local', 'nil', 'not', 'or', 'repeat',
	'return', 'then', 'true', 'until', 'while'
]

def create_lua_var(var, length=None):
	"""Return a valid Lua variable name."""
	valid = string.ascii_letters + string.digits + '_'
	if length is None:
		length = len(var)
	var = var.replace(' ', '_')

	i = 0
	while i < len(var) and i < length:
		if var[i] not in valid:
			var = var[:i] + var[i+1:]
		elif i == 0 and var[i] in string.digits:
			var = var[i+1:]
		else:
			i += 1
			
	var = var.lower()
	if var in LUA_KEYWORDS:
		var = '_' + var

	if len(var) == 0:
		var = None
	return var

class Dissector(object):
    """Dissector class is used to generate Wireshark dissectors written in Lua, for
    dissecting a packet into a set of fields with values."""

    def __init__(self, name, *args, **kwargs):
        """Create a new dissector instance."""
        self.name = name
        self.field_var = 'fields.'

class Protocol(object):
	
	# REGISTER_FUNC = 'delegator_register_proto'
	
	def __init__(self): # , name, id=None, description=None, *args, **kwargs
		self.var = 'proto'
		self.field_var = 'fields'
		
	def generate(self):
		"""Returns the Lua code for dissecting this protocol."""

		# Create dissector content.
		data = []
		data.append(self._header_definitions())
		data.append(self._field_definitions())
		data.append(self._dissector_function())
		data.append(self._register_dissector())
		return '\n'.join(i for i in data if i is not None)
		
	def _header_definitions(self):
		"""Add the code for the header of the protocol."""
		data = []
		comment = '-- Dissector for %s --' % Info.get_proto_name()
		data.append(comment)

		# Create a new protocol definition.
		proto = 'local {var} = Proto("{name}", "{description}")'
		data.append(proto.format(var=self.var, name=Info.get_proto_name(),
					description=Info.get_proto_desc()))
		# Create a new dissector table, if the dissector is to be a parent dissector.
		if Info.get_dissector_table() is not None:
			table = 'local {var} = DissectorTable.new("{tablename}", "{uiname}")'
			data.append(table.format(var=self.var + '_dt', tablename=Info.get_dissector_table(), uiname=Info.get_proto_name()))

		return '\n'.join(data)
		
	def _create_protofield(self, data, field, field_num, subf_num=None):
		"""Create a ProtoField definition for each protocol field and subfield."""
		field_var = self.field_var + '.f' + str(field_num)
		if subf_num != None:
			field_var = field_var + '_s' + str(subf_num)
		valstr_dict = field.get_valuestring()
		if valstr_dict:
			valstr = '{ '
			for key, val in valstr_dict.items():
				valstr += '[%i] = "%s", ' % (key, val)
			valstr += '}'
			data.append('local {var} = {values}'.format(var=field_var.split('.')[1] + '_valstr', values=valstr))

		template = '{var} = ProtoField.{type}("{proto_var}.{abbr}"{optionals})'
		args = {'var': field_var, 'type': field.get_type(), 'proto_var': self.var, 'abbr': field.get_abbr().lower()}

		# Add optional arguments, if specified.
		optional_args = []
		field_name = '"%s"' % field.get_name() if field.get_name() is not None else None
		field_desc = '"%s"' % field.get_desc() if field.get_desc() is not None else None
		for arg in [field_name, field.get_base(), field.get_bitmask(), field_desc]:
			if not arg:
				arg = 'nil'
			optional_args.append(arg)
		# Add also valuestring, if specified.
		if valstr_dict:
			optional_args.insert(2, field_var.split('.')[1] + '_valstr')
		else:
			optional_args.insert(2, 'nil')

		if optional_args:
			optional_args.insert(0, '')
			args['optionals'] = ', '.join(optional_args)
		else:
			args['optionals'] = ''

		return template.format(**args)

	def _field_definitions(self):
		"""Add the code for defining the fields of the protocol."""
		data = ['\n-- Protocol field definitions --']
		decl = 'local {field_var} = {var}.fields'
		data.append(decl.format(field_var=self.field_var, var=self.var))
		field_num = 0
		# Create a ProtoField definition for each protocol field.
		for field in Info.proto_fields:
			if len(Info.field_delimiter) == 0:
				field_num = field_num + 1
			elif len(Info.field_delimiter) > 0:
				try:
					field_num = Info.defined_delim_fields.index(True, field_num)
					field_num = field_num + 1 	# In Lua list indices start from 1, in Python from 0
				except ValueError:
					print 'ERROR: The size of Info.proto_fields is not equal to the size of Info.defined_delim_fields!'
			field_def = self._create_protofield(data, field, field_num)
			data.append(field_def)
			subfield_num = 0
			# Create a ProtoField definition also for each subfield.
			for subfield in field.subfields:
				if len(Info.field_delimiter) == 0:
					subfield_num = subfield_num + 1
				elif len(Info.field_delimiter) > 0:
					try:
						subfield_num = Info.defined_delim_subfields[field_num-1].index(True, subfield_num)
						subfield_num = subfield_num + 1 	# In Lua list indices start from 1, in Python from 0
					except ValueError:
						print 'ERROR: The size of field.subfields is not equal to the size of Info.defined_delim_subfields[field_num]!'
				subfield_def = self._create_protofield(data, subfield, field_num, subfield_num)
				data.append(subfield_def)

		# Add a ProtoField for the payload.
		payload_def = '{field_var}.payload = ProtoField.string("{proto_var}.payload", "Payload")'
		data.append(payload_def.format(field_var=self.field_var, proto_var=self.var))

		return '\n'.join(i for i in data if i is not None)
		
	def _handle_control_chars(self, delim):
		"""Checks the delimiter for control characters and adds an extra backslash
		in front of them. This way the control characters are written correctly to the
		dissector file in ASCII.
		"""
		# Replace '\t' with '\\t' so that it is printed correctly to the file.
		ind = -1
		for i in range(0, delim.count('09')):
			ind = delim.find('09', ind+1)
			delim = delim[:ind] + '5C 74' + delim[ind+2:]
		# Replace '\n' with '\\n' so that it is printed correctly to the file.
		ind = -1
		for i in range(0, delim.count('0A')):
			ind = delim.find('0A', ind+1)
			delim = delim[:ind] + '5C 6E' + delim[ind+2:]
		# Replace '\r' with '\\r' so that it is printed correctly to the file.
		ind = -1
		for i in range(0, delim.count('0D')):
			ind = delim.find('0D', ind+1)
			delim = delim[:ind] + '5C 72' + delim[ind+2:]

		return delim

	def _dissector_function(self):
		"""Add the code for the dissector function of the protocol."""
		data = ['\n-- Dissector function --']
		# Dissector function
		func_diss = 'function {var}.dissector(buffer, pinfo, tree)\n'
		data.append(func_diss.format(var=self.var))
		subtree = '\tlocal subtree = tree:add({var}, buffer())'
		data.append(subtree.format(var=self.var))
		t = '\tpinfo.cols.protocol = {var}.name'
		data.append(t.format(var=self.var))
		t = '\tpinfo.cols.info = {var}.description\n'
		data.append(t.format(var=self.var))

		## CASE: Fields have fixed lengths. ##
		if len(Info.field_delimiter) == 0:
			data.append('\tlocal packet = buffer():string()')
			# Add all fields to the protocol tree.
			field_num = 0
			for field in Info.proto_fields:
				field_num = field_num + 1
				field_var = self.field_var + '.f' + str(field_num)
				t = '\t'
				if len(field.subfields) > 0:
					t += 'local subsubtree_{name} = '
				t += 'subtree:add({var}, buffer({start},{length}))'
				data.append(t.format(name='f'+str(field_num), var=field_var,
							start=field.get_start(), length=field.get_length()))

				# Add all subfields to the protocol tree.
				subf_num = 0
				for subfield in field.subfields:
					subf_num = subf_num + 1
					subf_var = field_var + '_s' + str(subf_num)
					t = '\tsubsubtree_{name}:add({var}, buffer({start},{length}))'
					data.append(t.format(name='f'+str(field_num), var=subf_var, 
								start=subfield.get_start(), length=subfield.get_length()))

			# Add the code for handling the payload part of the packet.
			self._handle_payload(data)


		## CASE: Fields are separated by delimiters. ##
		elif len(Info.field_delimiter) > 0:
			data.append('\tlocal packet = buffer():string()')
			# Append defined fields table
			def_fields = '{'
			for val in Info.defined_delim_fields:
				if val == True:
					def_fields += 'true,'
				elif val == False:
					def_fields += 'false,'
			def_fields += '}'
			data.append('\tlocal def_fields = {table}'.format(table=def_fields))
			# Append defined subfields table
			def_subfields = '{ '
			for field in Info.defined_delim_subfields:
				def_subfields += '{'
				for subf in field:
					if subf == True:
						def_subfields += 'true,'
					elif subf == False:
						def_subfields += 'false,'
				def_subfields += '}, '
			def_subfields += '}'
			data.append('\tlocal def_subfields = {table}'.format(table=def_subfields))
			data.append('\t-- Delimiters --')
			t = '\tlocal field_delim = "{field_delim}"'

			delim = self._handle_control_chars(Info.field_delimiter)

			field_delim_ascii = binascii.unhexlify(delim.replace(' ', ''))
			data.append(t.format(field_delim=field_delim_ascii))
			t = '\tlocal subfield_delim = "{subfield_delim}"'

			delim = self._handle_control_chars(Info.subfield_delimiter)

			subfield_delim_ascii = binascii.unhexlify(delim.replace(' ', ''))
			data.append(t.format(subfield_delim=subfield_delim_ascii))
			data.append('\t-- Field variables --')
			data.append('\tlocal field = nil')
			data.append('\tlocal field_delim_start = nil')
			data.append('\tlocal field_delim_end = 1')
			data.append('\tlocal field_start = 1')
			data.append('\tlocal field_num = 1')

			data.append('\n\t-- Search fields separated by the field delimiter --')
			data.append('\trepeat')
			data.append('\t\tif field_delim:len() > 0 then')
			data.append('\t\t\tfield_delim_start, field_delim_end = packet:find(field_delim, field_delim_end)')
			data.append('\t\tend')
			data.append('\t\tif field_delim_start ~= nil then')
			data.append('\t\t\tfield = packet:sub(field_start, field_delim_end)')
			data.append('\t\t\tlocal subsubtree = nil')
			data.append('\t\t\tif def_fields[field_num] then')
			t = '\t\t\t\tsubsubtree = subtree:add({field_var}["f"..field_num], buffer(field_start-1, field:len()))'
			data.append(t.format(field_var=self.field_var))
			data.append('\t\t\tend')
			data.append('\t\t\t-- Subfield variables --')
			data.append('\t\t\tlocal subfield = nil')
			data.append('\t\t\tlocal subfield_delim_start = nil')
			data.append('\t\t\tlocal subfield_delim_end = nil')
			data.append('\t\t\tlocal subfield_start = field_start')
			data.append('\t\t\tlocal subfield_num = 1')
			data.append('\n\t\t\t-- Search subfields separated by the subfield delimiter inside the field --')
			data.append('\t\t\trepeat')
			data.append('\t\t\t\tif not def_fields[field_num] then break end')
			data.append('\t\t\t\tif subfield_delim:len() > 0 then')
			data.append('\t\t\t\t\tsubfield_delim_start, subfield_delim_end = packet:find(subfield_delim, subfield_start, field_delim_start-1)')
			data.append('\t\t\t\tend')
			data.append('\t\t\t\tif subfield_delim_start ~= nil and subfield_delim_end < field_delim_start then')
			data.append('\t\t\t\t\tsubfield = packet:sub(subfield_start, subfield_delim_start-1)')
			data.append('\t\t\t\t\tif def_subfields[field_num][subfield_num] then')
			t = '\t\t\t\t\t\tsubsubtree:add({field_var}["f"..field_num.."_s"..subfield_num], buffer(subfield_start-1, subfield:len()))'
			data.append(t.format(field_var=self.field_var))
			data.append('\t\t\t\t\tend')
			data.append('\t\t\t\t\tsubfield_num = subfield_num + 1')
			data.append('\t\t\t\t\tsubfield_start = subfield_delim_end + 1')
			data.append('\t\t\t\telseif subfield_num > 1 and def_subfields[field_num][subfield_num] then')
			data.append('\t\t\t\t\tsubfield = packet:sub(subfield_start, field_delim_start-1)')
			data.append('\t\t\t\t\tsubsubtree:add(fields["f"..field_num.."_s"..subfield_num], buffer(subfield_start-1, subfield:len()))')
			data.append('\t\t\t\tend')
			data.append('\t\t\tuntil subfield_delim_start == nil or subfield_delim_end >= field_delim_start')
			data.append('\n\t\t\tfield_num = field_num + 1')
			data.append('\t\t\tfield_start = field_delim_end + 1')
			data.append('\t\t\tfield_delim_end = field_delim_end + 1')
			data.append('\t\tend')
			data.append('\tuntil field_delim_start == nil')

			# Add the code for handling the payload part of the packet.
			self._handle_payload(data)


		# End the dissector function
		data.append('\nend')

		return '\n'.join(i for i in data if i is not None)

	def _handle_payload(self, data):
		# Payload start
		data.append('\n\t-- Handle the payload --')
		payload_start = 0
		if Info.header_length_from_last_field:
			last_field = Info.proto_fields[len(Info.proto_fields) - 1]
			payload_start = last_field.get_end() + 1
		elif Info.header_length is not None:
			payload_start = Info.header_length 	# Because (Wireshark) byte indexing starts from 0, no need to add 1.
		elif Info.header_delimiter is not None:
			t = '\tlocal header_delim = "{header_delim}"'
			header_delim = self._handle_control_chars(Info.header_delimiter[0])
			header_delim_ascii = binascii.unhexlify(header_delim.replace(' ', ''))
			data.append(t.format(header_delim=header_delim_ascii))
			data.append('\tlocal header_delim_start = nil')
			data.append('\tlocal header_delim_end = nil')
			data.append('\theader_delim_start, header_delim_end = packet:find(header_delim)')

		# Payload end
		payload_end = 0
		payload_length_field_start = None
		payload_length_field_end = None
		if Info.payload_delimiter is not None:
			t = '\tlocal payload_delim = "{payload_delim}"'
			payload_delim = self._handle_control_chars(Info.payload_delimiter[0])
			payload_delim_ascii = binascii.unhexlify(payload_delim.replace(' ', ''))
			data.append(t.format(payload_delim=payload_delim_ascii))
			data.append('\tlocal payload_delim_start = nil')
			data.append('\tlocal payload_delim_end = nil')
			if Info.header_delimiter is not None:
				data.append('\tpayload_delim_start, payload_delim_end = packet:find(payload_delim, header_delim_end+1)')
			else:
				t = '\tpayload_delim_start, payload_delim_end = packet:find(payload_delim, {payload_start})'
				data.append(t.format(payload_start=payload_start+1)) 	# Plus 1, because Lua indexing starts from 1.
		elif Info.payload_length_field_num is not None:
			field = Info.proto_fields[Info.payload_length_field_num]
			# Payload length is defined by a subfield.
			if Info.payload_length_subfield_num is not None:
				subfield = field.subfields[Info.payload_length_subfield_num]
				payload_length_field_start = subfield.get_start()
				payload_length_field_end = subfield.get_end()
			# Payload length is defined by a field.
			else:
				payload_length_field_start = field.get_start()
				payload_length_field_end = field.get_end()

		# Add the subdissector ID and address the payload to the subdissector.
		if Info.subdiss_field['field_num'] is not None:
			field_num = Info.subdiss_field['field_num']
			field = Info.proto_fields[field_num]
			# Subdissector ID is defined by a subfield.
			if Info.subdiss_field['subfield_num'] is not None:
				subf_num = Info.subdiss_field['subfield_num']
				subfield = field.subfields[subf_num]
				start = subfield.get_start()
				end = subfield.get_end()
			# Subdissector ID is defined by a field.
			else:
				field_delim_len = 0
				# The field delimiter must be removed from the field value.
				if len(Info.field_delimiter) > 0:
					field_delim_len = len(Info.field_delimiter.replace(' ', '')) / 2
				start = field.get_start()
				end = field.get_end() - field_delim_len
			length = end - start + 1
			t = '\tlocal subdiss_id = buffer({start_byte},{num_of_bytes}):uint()'
			data.append(t.format(start_byte=start, num_of_bytes=length))
			if Info.payload_length_use_rest:
				if Info.header_delimiter is not None:
					t = '\t{diss_table}:try(subdiss_id, buffer(header_delim_end):tvb(), pinfo, tree)'
					data.append(t.format(diss_table=self.var + '_dt'))
				else:
					t = '\t{diss_table}:try(subdiss_id, buffer({payload_start}):tvb(), pinfo, tree)'
					data.append(t.format(diss_table=self.var + '_dt', payload_start=payload_start))
			elif Info.payload_delimiter is not None:
				if Info.header_delimiter is not None:
					t = '\t{diss_table}:try(subdiss_id, buffer(header_delim_end, (payload_delim_end-1)-header_delim_end+1):tvb(), pinfo, tree)'
					data.append(t.format(diss_table=self.var + '_dt'))
				else:
					t = '\tlocal payload_start = {payload_start}'
					data.append(t.format(payload_start=payload_start))
					# Below, payload_delim_end has a Lua index but payload_start a Wireshark/Python index.
					t = '\t{diss_table}:try(subdiss_id, buffer(payload_start, (payload_delim_end-1)-payload_start+1):tvb(), pinfo, tree)'
					data.append(t.format(diss_table=self.var + '_dt'))
			elif Info.payload_length_field_num is not None:
				if Info.header_delimiter is not None:
					t = '\tlocal payload_length = buffer({start},{length}):uint()'
					data.append(t.format(start=payload_length_field_start, length=payload_length_field_end-payload_length_field_start+1))
					t = '\t{diss_table}:try(subdiss_id, buffer(header_delim_end, payload_length):tvb(), pinfo, tree)'
					data.append(t.format(diss_table=self.var + '_dt'))
				else:
					t = '\tlocal payload_length = buffer({start},{length}):uint()'
					data.append(t.format(start=payload_length_field_start, length=payload_length_field_end-payload_length_field_start+1))
					t = '\t{diss_table}:try(subdiss_id, buffer({payload_start}, payload_length):tvb(), pinfo, tree)'
					data.append(t.format(diss_table=self.var + '_dt', payload_start=payload_start))
		# Add the payload part as one field, if no subdissector.
		else:
			if Info.payload_length_use_rest:
				if Info.header_delimiter is not None:
					t = '\tsubtree:add({field_var}.payload, buffer(header_delim_end))'
					data.append(t.format(field_var=self.field_var))
				else:
					t = '\tsubtree:add({field_var}.payload, buffer({payload_start}))'
					data.append(t.format(field_var=self.field_var, payload_start=payload_start))
			elif Info.payload_delimiter is not None:
				if Info.header_delimiter is not None:
					t = '\tsubtree:add({field_var}.payload, buffer(header_delim_end, (payload_delim_end-1)-header_delim_end+1))'
					data.append(t.format(field_var=self.field_var))
				else:
					t = '\tlocal payload_start = {payload_start}'
					data.append(t.format(payload_start=payload_start))
					# Below, payload_delim_end has a Lua index but payload_start a Wireshark/Python index.
					t = '\tsubtree:add({field_var}.payload, buffer(payload_start, (payload_delim_end-1)-payload_start+1))'
					data.append(t.format(field_var=self.field_var))
			elif Info.payload_length_field_num is not None:
				if Info.header_delimiter is not None:
					t = '\tlocal payload_length = buffer({start},{length}):uint()'
					data.append(t.format(start=payload_length_field_start, length=payload_length_field_end-payload_length_field_start+1))
					t = '\tsubtree:add({field_var}.payload, buffer(header_delim_end, payload_length))'
					data.append(t.format(field_var=self.field_var))
				else:
					t = '\tlocal payload_length = buffer({start},{length}):uint()'
					data.append(t.format(start=payload_length_field_start, length=payload_length_field_end-payload_length_field_start+1))
					t = '\tsubtree:add({field_var}.payload, buffer({payload_start}, payload_length))'
					data.append(t.format(field_var=self.field_var, payload_start=payload_start))
		
	def _register_dissector(self):
		"""Add the code for registering the dissector in the parent dissector table."""
		if Info.get_parent_dissector_table():
			data = ['\n-- Dissector registration --']
			tbl_var = 'parent_dt'
			t = 'local {tbl_var} = DissectorTable.get("{parent_table}")'
			data.append(t.format(tbl_var=tbl_var, parent_table=Info.get_parent_dissector_table()))
			t = '{tbl_var}:add({diss_id}, {proto_var})'
			data.append(t.format(tbl_var=tbl_var, diss_id=Info.get_dissector_id(), proto_var=self.var))
			return '\n'.join(i for i in data if i is not None)

class Delegator(Dissector, Protocol):

	def __init__(self, *args, **kwargs):
		super(Delegator, self).__init__('custom_lua_dissectors', *args, **kwargs)
		self.field_var = 'f.'
		self.description = 'Custom Lua Dissectors'
		self.var = create_lua_var(self.name)
		if self.name:
			self.name = self.name.upper()
		else:
			self.name = 'delegator'
			self.var = 'DELEGATOR'
		self.table_var = create_lua_var(self.name + '_dt')
		self.id_table = create_lua_var('message_ids')
		self.size_table = create_lua_var('dissector_sizes')
		self.msg_var = create_lua_var('msg_node')

	def generate(self):
		"""Returns all the code for dissecting this protocol."""
		data = []
		data.append(self._header_definitions())
		data.append(self._field_definitions())
		data.append(self._register_function())
		data.append(self._dissector_function())
		return '\n'.join(i for i in data if i is not None)
		
	def _header_definitions(self):
		"""Add the code for the header of the protocol."""
		data = []
		comment = '-- Delegator for: %s' % self.name
		data.append(comment)

		# Create the delegator dissector.
		proto = 'local {var} = Proto("{name}", "{description}")'
		data.append(proto.format(var=self.var, name=self.name, 
					description=self.description))

		# Create the dissector table.
		t = 'local {var} = DissectorTable.new("{name}", "Custom Lua Dissectors", ftypes.STRING)'
		data.append(t.format(var=self.table_var, name=self.name))

		# Add the message id and dissector sizes tables.
		data.append('local {var} = {{}}'.format(var=self.id_table))
		data.append('local {var} = {{}}\n'.format(var=self.size_table))
		return '\n'.join(i for i in data if i is not None)
		
	def _register_function(self):
		"""Add code for register protocol function."""
		return """\
-- Register dissectors
function {func}(proto, name, id, sizes)
    {table}:add(name, proto)
    if id ~= nil then
        {id_table}[id] = name
    end
    if sizes ~= nil then
        for flag, size in pairs(sizes) do
            if {size_table}[flag] == nil then
                {size_table}[flag] = {{}}
            end
            if {size_table}[flag][size] == nil then
                {size_table}[flag][size] = {{}}
            end
            table.insert({size_table}[flag][size], name)
        end
    end
end\n""".format(func=self.REGISTER_FUNC, table=self.table_var,
				id_table=self.id_table, size_table=self.size_table)
				
	def _dissector_function(self):
		"""Add the code for the dissector function for the protocol."""
		data = []
		comment = '-- Delegator dissector function for %s' % self.name
		data.append(comment)
		
		# Add the dissector function.
		data.append('function {var}.dissector(buffer, pinfo, tree)'.format(var=self.var))
		data.append('\tlocal subtree = tree:add({var}, buffer())'.format(var=self.var))
		data.append('\tpinfo.cols.protocol = {var}.name'.format(var=self.var))
		data.append('\tpinfo.cols.info = {var}.description\n'.format(var=self.var))
		
		# Add the fields.
		data.append(self.version.get_code(0))
		data.append(self.flags.get_code(1))
		t = '\tpinfo.private.platform_flag = {flag}'
		data.append(t.format(flag=self.flags._value_var))
		data.append(self.msg_id.get_code(2, store=self.msg_var))
		t = '\tsubtree:add(f.messagelength, buffer(4):len()):set_generated()'
		data.extend([t, ''])
		
		# Find the message id and flag.
		msg_var = create_lua_var('id_value')
		data.append(self.msg_id._store_value(msg_var))
		data.append(self.length._store_value('length_value', offset=4))
		data.append('')

		# Call the right dissector.
		data.append('\t-- Call the correct dissector, or try and guess which')
		data.append('''\
	if {id_table}[{msg}] then
		{node}:append_text(" (" .. {id_table}[{msg}] ..")")
		{table}:try({id_table}[{msg}], buffer(4):tvb(), pinfo, tree)
	else
		{node}:add_expert_info(PI_MALFORMED, PI_WARN, "Unknown message id")
		if {size_table}[{flag}] and {size_table}[{flag}][{length}] then
			for key, value in pairs({size_table}[{flag}][{length}]) do
				{table}:try(value, buffer(4):tvb(), pinfo, tree)
			end
		end
	end\nend\n\n'''.format(id_table=self.id_table, msg=msg_var, node=self.msg_var,
							size_table=self.size_table, flag=self.flags._value_var,
							table=self.table_var, length=self.length._value_var))

		return '\n'.join(i for i in data if i is not None)


if __name__ == '__main__':
	pass
	