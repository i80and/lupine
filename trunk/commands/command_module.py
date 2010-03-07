import glob
import Command

class NoCompiler( Command.CommandError ):
	def __init__( self, var ):
		self.msg = 'No compiler given to {0}.'.format( var )
	
	def __str__( self ):
		return self.msg

class NoSourceError( Command.CommandError ):
	def __init__( self, var ):
		self.msg = 'No source specified for {0}.'.format( var )
	
	def __str__( self ):
		return self.msg

class InvalidSource( Command.CommandError ):
	def __init__( self, var, src ):
		self.msg = 'Invalid source {0} given to {1}.'.format( src, var )
	
	def __str__( self ):
		return self.msg

class command( Command.Command ):
	'''%module - Represent a source module in a program.
Valid options:
  * compiler - Compiler to use
  * src - List of modules to link.  Any raw source will be passed to a sub-module
  * options - Raw options to pass to the compiler
  * headersearch - Places to search for headers in
  * libs - List of %lib targets to link to/include
  * pic - Compile as position-independent; required for shared libraries.
  * packages - List of pkg-config packages to use
'''

	name = 'module'	
				
	def run( self ):
		'The actual execution stage.'
		self.verify()
		
		# Check for our deps and conflicts
		if not self:
			return
		
		if self.has_variable( 'optimize' ):
			optimize = self['optimize']
		else:
			optimize = ''
		
		# Set up the compiler
		if not self['compiler']:
			raise NoCompiler( self.reference_name )
			
		compiler = self['compiler']['compiler']
		
		# Get our platform
		self.set_child_command( 'platform', 'os' )
		
		# Check for source and expand wildcards
		src = []
		for srcfile in self['src']:
			if isinstance( srcfile, basestring ):
				src.extend( glob.glob( srcfile ))
			else:
				raise InvalidSourceError( srcfile, self.reference_name )

		# Add header data
		headersearch = []
		if self.has_variable( 'headersearch' ):
			for path in self['headersearch']:
				if isinstance( path, basestring ):
					headersearch.append( path )
		
		if self.has_variable( 'libs' ):
			for lib in self['libs']:
				if isinstance( lib, Command.Command ) and lib.name == 'lib':
					if lib.has_variable( 'headersearch' ):
						headersearch.extend( lib['headersearch'] )

		# Set up raw compile options
		options = []
		if self.has_variable( 'options' ):
			options = [self['options']]
		
		if self.has_variable( 'packages' ):
			for package in self['packages']:
				options.append( package['options'] )
		
		options = ' '.join( options )

		# Create our object-code rules
		objects = []
		for srcfile in src:
			target = self.env.escape_whitespace( compiler.name_obj( srcfile ))
			objects.append( target )
			escaped_src = self.env.escape_whitespace( srcfile )
			
			command = compiler.output_objcode( escaped_src, optimize, headersearch, self['pic'], options )
			deps = [self.env.escape_whitespace( dep ) for dep in self['compiler'].get_deps( srcfile )]
			self.env.make.add_rule( target, deps, command )
			
			self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))

		self.set_instance( 'output', objects )

	def verify( self ):
		if not self.has_variable( 'src' ):
			raise NoSourceError( self.reference_name )
		
		if not self.has_variable( 'pic' ):
			self['pic'] = False

	def __str__( self ):
		return 'module'
