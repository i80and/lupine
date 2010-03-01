import command_module
import Command

class command( command_module.command ):
	name = 'program'
	attributes = {	'src':list,
					'options':basestring,
					'target':basestring,
					'libs':list,
					'define':list,
					'depends':list,
					'conflicts':list
				}
				
	def run( self ):
		'The actual execution stage.'
		# Check for our deps and conflicts
		if not self:
			return

		# Get our platform
		self.set_child_command( 'platform', 'os' )

		# Set up our compiler
		if not self['compiler']:
			raise command_module.NoCompiler( self.reference_name )
			
		compiler = self['compiler']['compiler']

		# If we aren't given a target, just use our reference name
		if self.has_variable( 'target' ):
			target = self['target']
		else:
			target = self.reference_name

		# Check for modules to link in
		if not self.has_variable( 'src' ):
			raise command_module.NoSourceError( self.reference_name )
		
		# Add linking data
		libs = []
		if self.has_variable( 'libs' ):
			for lib in self['libs']:
				if isinstance( lib, basestring ):
					libs.append( lib )
				elif isinstance( lib, Command.Command ) and lib.name == 'lib':
					libs.extend( lib['link'] )

		# Set up raw compile options
		options = []
		if self.has_variable( 'options' ):
			options = [self['options']]
		
		if self.has_variable( 'packages' ):
			for package in self['packages']:
				options.append( package['options'] )
		
		options = ' '.join( options )
				
		# Look through the source, extracting and creating modules as needed
		modules = []
		raw_source = []
		for srcfile in self['src']:
			if isinstance( srcfile, basestring ):
				raw_source.append( srcfile )
			else:
				modules.extend( srcfile['output'] )
		
		# If there are source files in our list, compile them into a module
		if raw_source:
			module_name = '__module'
			self.set_child_command( 'module', module_name )
			module = self[module_name]
			module.set_instance( 'compiler', self['compiler'] )
			module.set_instance( 'src', raw_source )
			if self.has_variable( 'packages' ):
				module.set_instance( 'packages', self['packages'] )
			module.run()
			
			modules.extend( module['output'] )
		
		target = self.env.escape_whitespace( compiler.name_program( target ))
		command = compiler.output_program( modules, target, self['optimize'], libs, [], [] )
		self.env.make.add_rule( target, modules, command, default=True )
		
		self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))

	def __str__( self ):
		return 'program'
