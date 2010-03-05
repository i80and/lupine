import command_module
import Command

class command( Command.Command ):
	'''%lib - Define a library with shared libs and headers.
Valid options:
  * compiler - Compiler to use when testing
  * link - List of libraries to link against
  * libsearch - List of places to search for libraries in
  * headers - List of headers to check for
  * headersearch - List of places to check for headers in
  * required - Boolean of whether or not this library is required to exist or not
'''
	name = 'lib'

	def run( self ):
		'Check for the headers and shared objects for this library'
		# Verify to make sure we have valid options
		self.verify()

		# If no compiler is specified, fail
		if not self.has_variable( 'compiler' ):
			raise command_module.NoCompiler( self.reference_name )
		
		self.compiler = self['compiler']['compiler']	
		
		# Store whether or not all aspects of this library exist
		self.result = self.check_libs()
		if self.result:
			self.result = self.check_headers()

	def check( self, objs, msg, f ):
		'Generic check method'
		for x in objs:
			self.env.output.start( msg.format( x ))
			result = f( x )
			
			# Handle printing whether or not x was found
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
		libsearch = self['libsearch']
		
		if self.has_variable( 'link' ):
			return self.check( self['link'],
							'Checking for lib{0}...',
							lambda x: self.compiler.test_lib( x, libsearch ))
			
	def check_headers( self ):
		'Check if we can include the given libraries'
		headersearch = self['headersearch']
			
		if self.has_variable( 'headers' ):
			return self.check( self['headers'],
							'Checking for {0}...',
							lambda x: self.compiler.test_header( x, headersearch ))

	def verify( self ):
		'Verify options'
		# Required options
		if not self.has_variable( 'compiler' ):
			raise Command.CommandMissingOption( self.name, 'compiler' )
		
		# Type checks
		for option in ['link', 'libsearch', 'headers', 'headersearch']:
			if self.has_variable( option ):
				if not isinstance( self[option], list ):
					self[option] = [self[option]]
			else:
				self[option] = []
		
		if self.has_variable( 'required' ):
			if not isinstance( self['required'], bool ):
				self['required'] = True
		
	def __nonzero__( self ):
		return self.result
	
	def __str__( self ):
		return 'lib'
