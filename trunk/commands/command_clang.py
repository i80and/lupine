import command_gcc

class command( command_gcc.command ):
	'Clang compiler driver'
	name = 'clang'
			
	def __str__( self ):
		return 'clang'
