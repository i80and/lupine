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
	# No-op
	COMMENT = '#'
	# Textual token
	STRING = '"'

	# Regular expression to aid in parsing multi-word strings inside lists
	STRING_PAT = re.compile( ' "(.*)" |\s' )

	def __init__( self, path, env ):
		# Check argument types
		if not isinstance( path, basestring ):
			raise TypeError, path

		self.env = env

		# We use a two-stage parse: first stage assembles every assignment
		# into a single line (collapsing multi-line lists and strings), and
		# then the second stage performs the assignments.
		
		# TODO: Need a faster parser that can handle multi-line strings properly
		f = open( path, 'r' )
		lines = self.collapse( f )
		f.close()
		self.parse( lines )
				
	def parse( self, lines ):
		'Parse list of lines into a ProjectFile'
		for line in lines:
			line = line.strip()
			
			if not line or line[0] == self.COMMENT:
				continue
			
			splitline = line.split( ':' )
			
			# Make sure this line has a proper assignment
			if len( splitline ) < 2 or not splitline[1]:
				raise ParseExceptions.InvalidAssignment( line )
			
			var = splitline[0].strip()
			data = splitline[1].strip()
			
			self[var] = self.parse_data( var, data )
			
	def collapse( self, f ):
		'Collapse every assignment into a its own single line'
		lines = []
		buffer = []
		while True:
			line = f.readline()
			if not line:
				break
			
			line = line[:-1]
			
			# Buffer multi-line entries.  There are two cases this must take
			# place: a single double quote, or a single list-open
			open = line.find( self.LIST[0] )
			close = line.find( self.LIST[1], open+1 )
			
			if buffer:
				buffer.append( line )
				
				if close >= 0:
					# Close this and append it
					lines.append( ' '.join( buffer ))
					buffer = []
			
				continue
			
			if ( open >= 0 and close < 0 ):
				# Open this list
				buffer.append( line )
				continue
			
			lines.append( line )
		
		return lines

	def parse_data( self, var, data ):
		'Parse a string of data into a Python object'
		if data[0] == self.LIST[0]:
			# List			
			end = data.find( self.LIST[1] )
			data = self.STRING_PAT.split( data[1:end] )
			result = []
			
			for element in data:
				if element:
					result.append( self.parse_data( var, element ))
			
			return result
		elif data[0] == self.STRING:
			# String
			return data[1:-1]
		elif data[0] == self.OBJECT:
			# Load in a command object
			command = data[1:]
			try:
				return self.env.load_command( command, var )
			except Environment.NoSuchCommand as e:
				raise ParseExceptions.UnknownCommand( e.command, command )

		# Scaler of some kind; test boolean
		test = data.lower()
		if test == 'true':
			return True
		elif test == 'false':
			return False
		
		# Number?
		try:
			return float( test )
		except ValueError:
			pass
		
		# Plain string
		return data

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
