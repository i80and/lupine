class CDriverError( Exception ):
	def __init__( self, msg='' ):
		base = 'Error in the C Compiler driver'
		
		if msg:
			self.msg = '{0}: {1}.'.format( base, msg )
		else:
			self.msg = base + '.'

class SourceNotFound( CDriverError ):
	pass
