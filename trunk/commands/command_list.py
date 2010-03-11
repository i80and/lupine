import Command

class command( Command.Command ):
	'''%list - A list of arbitrary objects.  If it evaluates to true, it will
turn into a valid Python list.
Valid options:
  * contents - Items to store
'''
	name = 'list'
	def run( self ):
		contents = []
		if self:
			contents = self['contents']
	
		self.env.vars[self.reference_name] = contents
	
	def __str__( self ):
		return 'list'
