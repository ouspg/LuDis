##########################################
#   Module for checking the input file   #
#   that contains the sample packet.     #
#   Author: Jarmo Luomala (2013)         #
##########################################

import re, binascii

def check_file(filename):
	"""Check input file and verify its content.
	
	Checks that the file begins with HEX, BIN or ASC keyword,
	verifies the claimed content, and splits it into appropriate
	chunks.
	
	Returns integer (0=invalid, 1=HEX, 2=BIN, 3=ASCII) and the
	chunked file content or error message.
	
	Valid example hex file content:
	HEX 35 00 FF A2 81 9B E3
	"""
	file = open(filename, 'r')
	file_content = file.read()
	if len(file_content) < 3 or file_content.isspace():
		file.close()
		return (0, 'File content must begin with a keyword (HEX, BIN or ASC)!')
	# First 3 characters should represent the base of the content.
	base = file_content[0:3]
	file_content = file_content[3:]
	forbidden_chars = {'BIN': [None], 'HEX': [None]}

	# Content is claimed to be hexadecimal:
	if base == 'HEX':
		file_content = ''.join(file_content.split())
		file_content = file_content.upper()
		if len(file_content) < 2:
			file.close()
			return (0, 'File must contain at least 1 byte of data after the keyword!')
		mod = len(file_content) % 2
		if mod != 0:
			return (0, 'File must contain full bytes of data (2 hex digits = 1 byte)!')
		# Use regular expression for verifying the content.
		if re.match('[0-9A-F]+$', file_content):
			content = ''
			for start in range(0, len(file_content), 2):
				if start + 2 <= len(file_content):
					content += file_content[start:start+2] + ' '
				else:
					content += file_content[start:]		# add the remainings
			
			content = content.rstrip()		# remove possible whitespace at the end
			# Check that the file doesn't contain any forbidden control characters
			for val in content.split():
				if val in forbidden_chars['HEX']:
					file.close()
					return (0, 'File must not contain other control characters than TAB, LF or CR!')
			# Return type indicator and the chopped content.
			file.close()
			return (1, content)
		else:
			file.close()
			return (0, 'File content was invalid hexadecimal data!')
			
	# Content is claimed to be binary:
	elif base == 'BIN':
		file_content = ''.join(file_content.split())
		if len(file_content) < 8:
			file.close()
			return (0, 'File must contain at least 1 byte of data after the keyword!')
		mod = len(file_content) % 8
		if mod != 0:
			return (0, 'File must contain full bytes of data (8 bits = 1 byte)!')
			
		# Use regular expression for verifying the content.
		re.purge()		# clear regex cache
		if re.match('[0-1]+$', file_content):
			content = ''
			for start in range(0, len(file_content), 8):
				if start + 8 <= len(file_content):
					content += file_content[start:start+8] + ' '
				else:
					content += file_content[start:]		# add the remainings
					
			content = content.rstrip()		# remove possible whitespace at the end
			# Check that the file doesn't contain any forbidden control characters
			for val in content.split():
				if val in forbidden_chars['BIN']:
					file.close()
					return (0, 'File must not contain other control characters than TAB, LF or CR!')
			# Return type indicator and the chopped content.
			file.close()
			return (2, content)
		else:
			file.close()
			return (0, 'File content was invalid binary data!')
			
	# Content is claimed to be ASCII:
	elif base == 'ASC':
		escape_chars = ['\a', '\b', '\f', '\n', '\r', '\t', '\v']
		escape_letters = ['a', 'b', 'f', 'n', 'r', 't', 'v']
		# Use regular expression for verifying the content.
		re.purge()		# clear regex cache
		if re.match('[\x00-\x7F]+$', file_content):		# [\x20-\x7E]
			# Check that the file doesn't contain any forbidden control characters
			for c in file_content:
				if binascii.hexlify(c).upper() in forbidden_chars['HEX']:
					file.close()
					return (0, 'File contains illegal control characters!')
			for c in escape_chars:
				if file_content.count(c) != 0:
					file_content = file_content.replace(c, '')					
			# Replace all "\\n", "\\r" etc. with "\n", "\r" etc. (i.e. remove
			# the extra backslash) so that the control characters are interpreted
			# correctly into hex values.
			for c in range(0, len(file_content)):
				if file_content[c:c+1] == '\\':
					if file_content[c+1:c+2] in escape_letters:
						for e in escape_letters:
							if file_content[c+1:c+2] == e:
								file_content = file_content[:c] + escape_chars[escape_letters.index(e)] + file_content[c+2:]
								break
					else:
						return (0, 'File contains illegal control characters!\n\n' + 
								'Legal characters after a backslash are: a, b, f, n, r, t, and v.')

			# Return type indicator and the file content.
			file.close()
			return (3, file_content)
		else:
			file.close()
			return (0, 'File content was invalid ASCII data!')
		
	# Content is invalid:
	else:
		file.close()
		return (0, 'File content must begin with a keyword (HEX, BIN or ASC)!')


if __name__ == '__main__':
	filename = './sample-input-files/hex.txt'
	type, content = check_file(filename)
	if type == 0:
		print 'File content is invalid!'
		print 'ERROR: %s' % content
	elif type == 1:
		print 'File content is HEX.'
		print 'Chopped content: %s' % content
	elif type == 2:
		print 'File content is BIN.'
		print 'Chopped content: %s' % content
	elif type == 3:
		print 'File content is ASCII.'
		print 'Chopped content: %s' % content