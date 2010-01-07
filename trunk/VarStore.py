import re
import ParseExceptions

class VarStore( dict ):
	var_regexp = re.compile( '\\$\\(([a-zA-Z_.\-]+)\\)' )

	def __init__( self ):
		dict.__init__( self )

	def __str__( self ):
		return 'VarStore({0})'.format( self.keys())

	def __getitem__( self, key ):
		if dict.has_key( self, key ):
			# Try to get the value from the local scope
			value = dict.__getitem__( self, key )
		else:
			# We can't find this key through normal means.  If this refers to
			# an object member, dereference it and check that in case of a static
			# variable
			splitkey = key.split( '.' )
			if len( splitkey ) > 1:
				return self[splitkey[0]]['.'.join( splitkey[1:] )]
			raise ParseExceptions.NoMatchingVariable( key )
		
		if isinstance( value, basestring ):
			value = self.__subs_var( value )
		elif isinstance( value, list ):
			value = [self.__subs_var( x ) for x in value]

		return value
		
	def __subs_var( self, value ):
		'Substitute any variables in a given string'
		if not isinstance( value, basestring ):
			return value
		
		var_matches = self.var_regexp.findall( value )
		for match in var_matches:
			varstr = '$({0})'.format( match )

			# If this variable is the only thing in this token, return it raw.  Otherwise,
			# turn it into a string and splice it in
			if not value.replace( varstr, '' ):
				value = self[match]
			else:
				try:
					# Substitute the variable and parse it into a natural Python object
					if isinstance( value, basestring ):
						newentry = str( self[match] )
					else:
						newentry = self[match]
					value = value.replace( varstr, newentry )
				except KeyError:
					pass
		
		return value


	# Should these be moved into Environment?
	def set_var( self, obj, var, value ):
		'Add a command-level variable'
		target_name = self.var_name( obj, var )
		self[target_name] = value
	
	def var_name( self, obj, var ):
		'Get a variable name from a given object and variable'
		return '{0}.{1}'.format( obj, var )
