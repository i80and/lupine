import Command
import command_lib
import LinkedTargetGenerator

class NonPicSource( Command.CommandError ):
	def __init__( self, name ):
		self.name = name
	
	def __str__( self ):
		return 'Non-PIC (Position Independent) source given to {0};	\
		set {0}.pic: True.'.format( self.name )

class command( LinkedTargetGenerator.LinkedTargetGenerator ):
	'''%shared - Represent a C-like program.
Valid options:
  * compiler - Compiler to use
  * src - List of modules to link.  Any raw source will be passed to a sub-module
  * options - Raw options to pass to the compiler
  * target - Output name
  * libs - List of %lib targets to link to/include
'''
	name = 'shared'
	compilation_method = 'output_shared'
	target_name_gen = 'name_shared'

	def make_submodule( self, src ):
		'Create a submodule for loose source files'		
		module_name = '__module'
		self.set_child_command( 'module', module_name )
		module = self[module_name]
		module.set_instance( 'compiler', self['compiler'] )
		module.set_instance( 'src', src )
		module.set_instance( 'pic', True )
		if self.has_variable( 'libs' ):
			module.set_instance( 'libs', self['libs'] )
		if self.has_variable( 'packages' ):
			module.set_instance( 'packages', self['packages'] )
		module.run()
		
		return module['output']

	def verify( self ):
		LinkedTargetGenerator.LinkedTargetGenerator.verify( self )
		
		# Make sure that all of our modules are PIC
		for srcfile in self['src']:
			if isinstance( srcfile, command_lib.command ) and not srcfile['pic']:
				raise NonPicSource( self.reference_name )

	def __str__( self ):
		return 'shared'
