import re
import Command
import Environment
import ParseExceptions

class ProjectFile:
	list_regexp = re.compile( '\s' )

	# Encases a list
	LIST = ('[', ']')
	# Denotes an object definition
	OBJECT = '%'
	# Denotes an attribute of an object
	ATTR = '.'

	def __init__( self, path, env ):
		# Check argument types
		if not isinstance( path, basestring ):
			raise TypeError, path

		self.env = env
		
		# List processing variables
		# liststart is needed for potential debugging in case the user forgets
		# to close a list.
		liststart = ''
		curlist = []
		value = None
		
		# Open the project file
		f = open( path, 'r' )
		for line in f.readlines():
			# Skip empties and comments
			line = line.strip()
			if( not len( line ) or line[0] == '#' ):
				continue

			if not curlist:
				# What to do if we're not in the middle of parsing a list
				splitline = line.split( ':', 1 )
				splitline = [lineseg.strip() for lineseg in splitline]
				var = splitline[0]
				data = splitline[1]
				
				# No assignment is taking place here; shouldn't just
				# skip over it because it's probably a typo
				if len( splitline ) <= 1 or not data:
					raise ParseExceptions.ParseError, var
				
				if data[0] == self.LIST[0]:
					# Start a list
					# See if it's all on this line
					if data[-1] == self.LIST[1]:
						try:
							self[var] = self.parseList( data )
						except ParseExceptions.UnclosedString as e:
							e.set_location( 'In assignment: {0}'.format( liststart ))
							raise e

					else:
						liststart = var
						curlist.append( data )					
				elif data[0] == self.OBJECT:
					# Create an object if this isn't a command name
					try:
						self[var] = self.env.load_command( data[1:], var )
					except Environment.NoSuchCommand as e:
						raise ParseExceptions.UnknownCommand( e.command, splitline[0] )
				else:
					# Just a plain value					
					# If this is an object attribute, check it for validity
					var_objs = var.split( '.' )
					parsed_data = self.parseValue( data )
					if len( var_objs ) > 1:
						obj = '.'.join( var_objs[0:-1] )
						if not self.env.has_command( obj ):
							required_type = self[obj].attributes[var_objs[-1]]
							if not isinstance( parsed_data, required_type ):
								raise ParseExceptions.WrongDataType( var, required_type.__name__ )
					else:
						if self.env.has_command( var ):
							raise ParseExceptions.ReservedVariable( var )
					
					self[var] = parsed_data
			else:
				# We are in fact inside a list definition
				curlist.append( line )
				
				if line[-1] == self.LIST[1]:
					# End and parse a list
					try:
						self[liststart] = self.parseList( ' '.join( curlist ))
					except ParseExceptions.UnclosedString as e:
						e.set_location( 'In assignment: {0}'.format( liststart ))
						raise e
					curlist = []

		# Check for unended lists
		if curlist:
			raise ParseExceptions.UnclosedList( 'In assignment: {0}'.format( liststart ))
		
		f.close()
		
	def parseValue( self, val ):
		'Parse a string value into a Python type.'
		if not isinstance( val, basestring ):
			raise TypeError, val
		
		# Lowercase it, check for boolean
		testVal = val.lower()
		if testVal == 'true':
			return True
		elif testVal == 'false':
			return False
		
		# Check for numerical value
		try:
			return float( val )
		except ValueError:
			pass
		
		# See if it is encased in quotes; if so, strip them off
		if val[0] == '"' and val[-1] == '"':
			return val[1:-1]
		
		# It's probably a string; just return it raw
		return val

	def parseList( self, value ):
		'Parse a string into a whitespace-seperated list.'
		# Chop off the starting and ending list markers
		value = value.strip()[1:-1].strip()
		
		# Do a simple split
		values = self.list_regexp.split( value )

		# Accumulate, keeping quotes in mind
		# TODO: Quote escaping of some form
		# TODO: Allow list nesting
		results = []
		accumulater = []
		for entry in values:
			if not entry:
				continue
		
			# Check for the start of a jumbo token
			if( entry[0] == '"' ):
				accumulater = [entry[1:]]
			elif accumulater:
				if( entry[-1] == '"' ):
					# Append this token sans ending quote, and add the whole thing
					end_index = len( entry ) - 1
					accumulater.append( entry[0:end_index] )
					results.append( ' '.join( accumulater ))
					accumulater = []
				else:
					# Append this token, don't strip off anything
					accumulater.append( entry )
			else:
				results.append( self.parseValue( entry ))
		
		# Check for quotes that are still open
		if accumulater:
			raise ParseExceptions.UnclosedString()

		return results

	@property
	def variables( self ):
		return self.env.variables()

	def __len__( self ):
		return len( self.vars )

	def __getitem__( self, key ):
		return self.env[key]
	
	def __setitem__( self, key, value ):
		# See if we have to set an object attribute
		attr_split = key.split( self.ATTR )
		if len( attr_split ) > 1:
			try:
				if key[0] == self.OBJECT:
					# Set a variable globally for this object
					command_name = attr_split[0][1:]
					var_name = attr_split[1]
					self.env.vars.set_var( command_name, var_name, value )
				else:
					# Make sure we're actually dealing with an object
					try:
						if self.env.has_command( attr_split[0] ):
							self.env[key] = value
							return
						if not isinstance( self.env[attr_split[0]], Command.Command ):
							raise ParseExceptions.MemberAssignmentToNonObject( key )
					except KeyError:
						raise ParseExceptions.NoMatchingVariable( attr_split[0] )
			
					# Set a varable just for this object
					self.env[attr_split[0]].set_instance( attr_split[1], value )
			except ParseExceptions.NoSuchAttribute as e:
				raise ParseExceptions.NoSuchAttribute( e.attribute )
			
			return

		# Simple case; no objects involved
		self.env[key] = value

	def __iter__( self ):
		return iter( self.env )
