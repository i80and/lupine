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
	name = 'module'	
	attributes = { 'src':list,
					'options':basestring,
					'define':list,
					'depends':list,
					'conflicts':list,
					'packages':list
				}
				
	def run( self ):
		'The actual execution stage.'
		# Check for our deps and conflicts
		if not self:
			return
		
		# Set up the compiler
		if not self['compiler']:
			raise NoCompiler( self.reference_name )
			
		compiler = self['compiler']['compiler']
		
		# Get our platform
		self.set_child_command( 'platform', 'os' )
		
		# Check for source and expand wildcards
		if not self['src']:
			raise NoSourceError( self.reference_name )
		
		src = []
		for srcfile in self['src']:
			if isinstance( srcfile, basestring ):
				src.extend( glob.glob( srcfile ))
			else:
				raise InvalidSourceError( srcfile, self.reference_name )

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
			
			command = compiler.output_objcode( escaped_src, self['optimize'], [], options )
			deps = [self.env.escape_whitespace( dep ) for dep in self['compiler'].get_deps( srcfile )]
			self.env.make.add_rule( target, deps, command )
			
			self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))

		self.set_instance( 'output', objects )

	def __nonzero__( self ):
		if self['depends']:
			for dep in self['depends']:
				if not dep:
					return False
		
		if self['conflicts']:
			for conflict in self['conflicts']:
				if conflict:
					return False
		
		return True
	
	def __str__( self ):
		return 'module'
