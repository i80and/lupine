import Command

class command( Command.Command ):
	name = 'null'
	def run( self ):
		'The actual execution stage.'
		pass
	
	def __str__( self ):
		return 'null'
