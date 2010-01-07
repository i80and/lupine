import command_cc

class command( command_cc.command ):
	'GCC compiler driver'
	name = 'gcc'
			
	def output_shared( self, dest ):
		return '-shared -fPIC -o {0}.so'.format( dest )
	
	def optimize( self, level ):
		if level == 0:
			return '-O1'
		elif level == 1 or level == True:
			return '-O2 -s'
		elif level == 2:
			return '-O3 -s'
		else:
			return ''
		
	def debug( self ):
		return '-O0 -g -Wall'
		
	def __str__( self ):
		return 'gcc'
