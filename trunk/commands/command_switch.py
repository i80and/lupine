import Command

class command( Command.Command ):
	'''%switch - Set self to first object in .options to evaluate as true
Valid options:
  * options - List of choices.
'''
	name = 'switch'
	
	def run( self ):
		'The actual execution stage.'
		# Verify to make sure we have valid options
		self.verify()
		
		for entry in self['options']:
			if entry:
				self.env.vars[self.reference_name] = entry
				return

		self.env.vars[reference_name] = None

	def verify( self ):
		'Verify options'
		if not self.has_variable( 'options' ):
			raise Command.CommandMissingOption( self.name, 'options' )
		
		if not isinstance( self['options'], list ):
			self.set_instance( 'options', [self['options']] )
	
	def __str__( self ):
		return self.name
