##############################################
#   Methods for converting the SEL indices   #
#   to nibbles/bytes, and vice versa.        #
#   Author: Jarmo Luomala (2013)             #
##############################################

def sel_from_hex(first, last, as_nibbles=False):
	"""Returns the index of the first and the last nibble
	or byte corresponding the highlighted area.
	"""
	first = int(str(first)[2:])	# remove '1.' from the beginning
	last = int(str(last)[2:])	# and convert to integer
	last -= 1					# last byte/nibble is behind the marker
	
	# Move the last marker backwards if it points to a gap.
	if last % 3 == 2:
		last -= 1
		
	first_nibble = first - (first / 3)
	last_nibble = last - (last / 3)
	first_byte = first_nibble / 2
	last_byte = last_nibble / 2

	if not as_nibbles:
		return (first_byte, last_byte)
	else:
		return (first_nibble, last_nibble)

def sel_from_bin(first, last, as_nibbles=False):
	"""Returns the index of the first and the last nibble
	or byte corresponding the highlighted area.
	"""
	first = int(str(first)[2:])	# remove '1.' from the beginning
	last = int(str(last)[2:])	# and convert to integer
	last -= 1					# last byte/nibble is behind the marker

	# Bytes initially inside the selection.
	first_byte = (first + 1) / 9
	last_byte = last / 9
	# Correction: at least two of the byte's bits must be chosen
	# for the byte to be selected.
	if first_byte < last_byte:
		if first % 9 > 6:
			first_byte += 1
		if (last + 1) % 9 < 2:	# (last + 1) because that's where the highlight ends
			last_byte -= 1
	# If first and last bytes were adjacent, and both were
	# moved past each other.
	if first_byte > last_byte:
		return (None, None)
	
	# Count the nibble values.
	first_nibble = 2 * first_byte
	if first % 9 > 2:
		first_nibble += 1	# first nibble is the second nibble
							# of the first byte
	last_nibble = 2 * last_byte
	if (last + 1) % 9 > 5:
		last_nibble += 1	# last nibble is the second nibble
							# of the last byte
	# First and last nibbles are in the same byte, and first
	# nibble value was incremented past the last nibble.
	if first_nibble > last_nibble:
		return (None, None)

	if not as_nibbles:
		return (first_byte, last_byte)
	else:
		return (first_nibble, last_nibble)

def sel_from_ascii(first, last):
	"""Returns the index of the first and the last nibble
	or byte corresponding the highlighted area.
	"""
	first_byte = int(str(first)[2:])	# remove '1.' from the beginning
	last_byte = int(str(last)[2:])		# and convert to integer
	last_byte -= 1						# last byte/nibble is behind the marker
	return (first_byte, last_byte)

def nibbles_to_sel(first_nibble, last_nibble, format):
	first_byte = first_nibble / 2
	last_byte = last_nibble / 2
	
	if format == 'BIN':
		sel_first = first_byte * 9
		# Check if the first nibble is the second nibble of the first byte.
		if first_nibble % 2 == 1:
			sel_first += 4
		sel_last = last_byte * 9 + 4
		# Check if the last nibble is the second nibble of the last byte.
		if last_nibble % 2 == 1:
			sel_last += 4
	elif format == 'HEX':
		sel_first = first_byte * 3
		if first_nibble % 2 == 1:
			sel_first += 1
		sel_last = last_byte * 3 + 1
		if last_nibble % 2 == 1:
			sel_last += 1
	elif format == 'ASCII':
		sel_first, sel_last = first_byte, last_byte + 1
	else:
		return (None, None)
	
	sel_first = '1.' + str(sel_first)
	sel_last = '1.' + str(sel_last)
	return (sel_first, sel_last)
	

if __name__ == '__main__':
	# DEBUG
	first, last = sel_from_bin('1.6', '1.20', True)
	#first, last = nibbles_to_sel(2, 5, 'BIN')
	#first, last = nibbles_to_sel(0, 2, 'HEX')
	print 'First:', first, 'Last:', last
	