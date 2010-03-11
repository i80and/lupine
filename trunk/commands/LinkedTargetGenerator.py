import command_lib
import Command

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

class LinkedTargetGenerator( Command.Command ):
	'A generic C-style target generator, to be used by %program and %shared.'
	name = 'LinkedTargetGenerator'
	
	# This is the method that will be called 
	compilation_method = None
	
	# This method will determine the output filename based on a base
	target_name_gen = None
	
	def run( self ):
		'The actual execution stage.'
		self.verify()
		
		# Check for our deps and conflicts
		if not self:
			return

		# Get our platform
		self.set_child_command( 'platform', 'os' )

		# Add linking data
		libs = []
		libsearch = []
		headersearch = []
		if self.has_variable( 'libs' ):
			for lib in self['libs']:
				if isinstance( lib, command_lib.command ):
					libs.extend( lib['link'] )
					if lib.has_variable( 'libsearch' ):
						libsearch.extend( lib['libsearch'] )
					if lib.has_variable( 'headersearch' ):
						headersearch.extend( lib['headersearch'] )
		
		# Set up raw compile options
		options = []
		if self.has_variable( 'options' ):
			options = [self['options']]
		
		if self.has_variable( 'packages' ):
			for package in self['packages']:
				options.append( package['options'] )
		
		# Create Make targets to create our object code
		outputs = []
		for srcfile in self['src']:
			outputs.extend( self.compile( srcfile, headersearch, options ))
		
		# Link all of our object code
		self.link( outputs, libs, libsearch, options )

	def compile( self, src, headersearch, options ):
		'Generate object code from our source files'
		objects = []
		compiler = self['compiler']['compiler']
				
		if not isinstance( src, list ):
			src = [src]
		
		pic = False
		if self.has_variable( 'pic' ):
			pic = self['pic']
		
		for srcfile in src:
			if not isinstance( srcfile, basestring ):
				continue
			target = self.env.escape_whitespace( compiler.name_obj( srcfile ))
			objects.append( target )
			escaped_src = self.env.escape_whitespace( srcfile )
			
			command = compiler.output_objcode( escaped_src, self['optimize'], headersearch, pic, options )
			deps = [self.env.escape_whitespace( dep ) for dep in self['compiler'].get_deps( srcfile )]
			self.env.make.add_rule( target, deps, command )
			
			self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))

		return objects
	
	def link( self, objects, libs, libsearch, options ):
		'Generate a binary from our object code'
		compiler = self['compiler']['compiler']
		
		# Create our make command
		name_gen = getattr( compiler, self.target_name_gen )
		target = self.env.escape_whitespace( name_gen( self['target'] ))
		
		# Generically call whatever's needed to output the appropriate
		# linked result.
		compilation_command = getattr( compiler, self.compilation_method )
		command = compilation_command( objects, target, self['optimize'], libs, libsearch, options )
		
		self.env.make.add_rule( target, objects, command, default=True )
		
		self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))

	def verify( self ):
		if not self.has_variable( 'compiler' ):
			raise NoCompiler( self.reference_name )
		
		if not self.has_variable( 'src' ):
			raise NoSourceError( self.reference_name )

		if not self.has_variable( 'optimize' ):
			self['optimize'] = ''

		# Set our default target
		if not self.has_variable( 'target' ):
			name_gen = getattr( self['compiler']['compiler'], self.target_name_gen )
			self['target'] = name_gen( self.reference_name )

	def __str__( self ):
		return self.name
