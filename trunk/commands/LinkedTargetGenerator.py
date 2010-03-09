import command_lib
import command_module
import Command

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

		if self.has_variable( 'optimize' ):
			optimize = self['optimize']
		else:
			optimize = ''

		# Get our platform
		self.set_child_command( 'platform', 'os' )

		# Set up our compiler
		if not self['compiler']:
			raise command_module.NoCompiler( self.reference_name )
			
		compiler = self['compiler']['compiler']

		# If we aren't given a target, just use our reference name
		target = self['target']

		# Check for modules to link in
		if not self.has_variable( 'src' ):
			raise command_module.NoSourceError( self.reference_name )
		
		# Add linking data
		libs = []
		libsearch = []
		if self.has_variable( 'libs' ):
			for lib in self['libs']:
				if isinstance( lib, command_lib.command ):
					libs.extend( lib['link'] )
					if lib.has_variable( 'libsearch' ):
						libsearch.extend( lib['libsearch'] )
		
		# Set up raw compile options
		options = []
		if self.has_variable( 'options' ):
			options = [self['options']]
		
		if self.has_variable( 'packages' ):
			for package in self['packages']:
				options.append( package['options'] )
		
		# Look through the source, extracting and creating modules as needed
		modules = []
		raw_source = []
		for srcfile in self['src']:
			if isinstance( srcfile, basestring ):
				raw_source.append( srcfile )
			elif isinstance( srcfile, Command.Command ):
				if srcfile.has_variable( 'output' ):
					modules.extend( srcfile['output'] )
				elif srcfile.has_variable( 'target' ):
					modules.append( srcfile['target'] )
		
		# If there are source files in our list, compile them into a module
		if raw_source:
			modules.extend( self.make_submodule( raw_source ))
			
		# Create our make command
		name_gen = getattr( compiler, self.target_name_gen )
		target = self.env.escape_whitespace( name_gen( target ))
		
		# Generically call whatever's needed to output the appropriate
		# linked result.
		compilation_command = getattr( compiler, self.compilation_method )
		command = compilation_command( modules, target, optimize, libs, libsearch, options )
		
		self.env.make.add_rule( target, modules, command, default=True )
		
		self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))

	def make_submodule( self, src ):
		'Create a submodule for loose source files'
		module_name = '__module'
		self.set_child_command( 'module', module_name )
		module = self[module_name]
		module.set_instance( 'compiler', self['compiler'] )
		module.set_instance( 'src', src )
		if self.has_variable( 'libs' ):
			module.set_instance( 'libs', self['libs'] )
		if self.has_variable( 'packages' ):
			module.set_instance( 'packages', self['packages'] )
		module.run()
		
		return module['output']

	def verify( self ):
		if not self.has_variable( 'compiler' ):
			raise Command.CommandMissingOption( self.reference_name, 'compiler' )
		
		if not self.has_variable( 'src' ):
			raise NoSourceError( self.reference_name )

		# Set our default target
		if not self.has_variable( 'target' ):
			name_gen = getattr( self['compiler']['compiler'], self.target_name_gen )
			self['target'] = name_gen( self.reference_name )

	def __str__( self ):
		return self.name
