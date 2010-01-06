import re

space_regexp = re.compile( '\s' )

def escape( str ):
	'Escape whitespace in a string.'
	return space_regexp.sub(( lambda s: '\\' + s.group()), str )
