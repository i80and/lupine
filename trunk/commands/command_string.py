import Command

class command( Command.Command ):
	'''%string - A string wrapper.  If it evaluates to true, it will turn into
a valid Python string.
Valid options:
  * contents - String to store.
'''
	name = 'string'
	
	def run( self ):
		contents = ''
		if self:
			contents = self['contents']
	
		self.env.vars[self.reference_name] = contents
	
	def __str__( self ):
		return 'string'
