class ParseError( Exception ):
	def __init__( self, msg='' ):
		self.msg = msg
	
	def __str__( self ):
		return self.msg

class UnclosedString( ParseError ):
	def __init__( self, msg='' ):
		self.msg = 'String never closed'

		if msg:
			self.set_location( msg )	
	
	def set_location( self, loc ):
		self.msg += ' - {0}'.format( loc )

class UnclosedList( ParseError ):
	def __init__( self, msg='' ):
		base = 'List never closed'
		if not msg:
			self.msg = base
		else:
			self.msg = '{0} - {1}'.format( base, msg )

class UnknownCommand( ParseError ):
	def __init__( self, command, loc='' ):
		base = 'Unknown command'
		if not loc:
			self.msg = '{0}: {1}'.format( base, command )
		else:
			self.msg = '{0}: {1} in assignment to {2}'.format( base, command, loc )

class NoMatchingVariable( ParseError ):
	def __init__( self, variable='' ):
		base = 'No matching variable'
		if not variable:
			self.msg = base
		else:
			self.msg = '{0}: {1}'.format( base, variable )
	
class MemberAssignmentToNonObject( ParseError ):
	def __init__( self, variable='' ):
		base = 'Assignment to non-object'
		if not variable:
			self.msg = base
		else:
			self.msg = '{0}: {1}'.format( base, variable )

class NoSuchAttribute( ParseError ):
	def __init__( self, attribute='' ):
		base = 'Assignment to non-existent attribute'
		if not attribute:
			self.msg = base
		else:
			self.msg = '{0}: {1}'.format( base, attribute )

class WrongDataType( ParseError ):
	def __init__( self, variable, required='' ):
		base = 'Wrong data type in variable: {0}'
		self.msg = base.format( variable )

		if required:
			self.msg = '{0}.  Needs to be {1}'.format( self.msg, required )

class ReservedVariable( ParseError ):
	def __init__( self, var='' ):
		base = 'Assignment to reserved variable'
		if not var:
			self.msg = base
		else:
			self.msg = '{0}: {1}'.format( base, var )
