import LinkedTargetGenerator

class command( LinkedTargetGenerator.LinkedTargetGenerator ):
	'''%program - Represent a C-like program.
Valid options:
  * compiler - Compiler to use
  * src - List of modules to link.  Any raw source will be passed to a sub-module
  * options - Raw options to pass to the compiler
  * target - Output name
  * libs - List of %lib targets to link to/include
'''
	name = 'program'
	compilation_method = 'output_program'
	target_name_gen = 'name_program'

	def __str__( self ):
		return 'program'
