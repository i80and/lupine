import Command

class command( Command.Command ):
	name = 'switch'
	attributes = {'options':list}
	
	def run( self ):
		'The actual execution stage.'
		for entry in self['options']:
			if entry:
				self.env.vars[self.reference_name] = entry
				return

		self.env.vars[reference_name] = None
	
	def __str__( self ):
		return self.name
