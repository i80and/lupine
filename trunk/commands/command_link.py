import Command

class command( Command.Command ):
	name = 'link'
	def run( self ):
		'The actual execution stage.'
		self.set_child_command( 'c', 'compiler' )
		compiler = self['compiler']	
		
		# See if we've already found out about this library
		name = self['name']
		if self.has_variable( name ):
			return
		
		self.env.output.start( 'Checking for lib{0}...'.format( name ))
		self.set_instance( 'result',  self['compiler'].test_lib( name ))

		if self['result']:
			self.env.output.success( 'found' )
		else:
			if self['required']:
				self.env.output.error( 'not found' )
			else:
				self.env.output.warning( 'not found' )
		
		self.set_static( name, self['result'] )
	
	def eval( self ):
		return self['result']
	
	def __str__( self ):
		return 'link'
