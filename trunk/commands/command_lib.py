import command_module
import Command

class command( Command.Command ):
	name = 'lib'
	attributes = {'link':list,
					'libsearch': list,
					'headers': list,
					'headersearch': list,
					'required': bool
				}
	
	def run( self ):
		'Check for the headers and shared objects for this library'
		# If no compiler is specified, fail
		if not self.has_variable( 'compiler' ):
			raise command_module.NoCompiler( self.reference_name )
		
		self.compiler = self['compiler']['compiler']	
		
		# Store whether or not all aspects of this library exist
		self.result = self.check_libs()
		if self.result:
			self.result = self.check_headers()

	def check( self, objs, msg, f ):
		for x in objs:
			self.env.output.start( msg.format( x ))
			result = f( x )
			
			if not result:
				if self['required']:
					self.env.output.error( 'not found' )
				else:
					self.env.output.warning( 'not found' )
				return False
	
			self.env.output.success( 'found' )			
		return True

	def check_libs( self ):
		'Check if we can link to the given libraries'
		if self.has_variable( 'link' ):
			return self.check( self['link'],
							'Checking for lib{0}...',
							lambda x: self.compiler.test_lib( x, self['libsearch'] ))
			
	def check_headers( self ):
		'Check if we can include the given libraries'
		if self.has_variable( 'headers' ):
			return self.check( self['headers'],
							'Checking for {0}...',
							lambda x: self.compiler.test_header( x, self['headersearch'] ))
		
	def __nonzero__( self ):
		return self.result
	
	def __str__( self ):
		return 'lib'
