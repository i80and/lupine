import os
import Command

class command( Command.Command ):
	'''%platform - Represent the current platform, and give information on it.
Valid options:
  * unsupported - List of unsupported platforms
  * supported - List of exclusively-supported platforms
'''

	name = 'platform'
	attributes = {'supported': list, 'unsupported': list}
	
	def __init__( self, env, var_name ):
		'Get the operating system being run.'
		Command.Command.__init__( self, env, var_name )
		if not self.has_variable( 'os' ):
			self.set_os()
			self.set_core()
		
	def set_os( self ):
		'Find the operating system information'
		name = os.name
		detailed_name = os.uname()[0].lower()
		
		os_sequence = [name, None]
		
		self.set_static( name, True )
	
		if name == 'posix':
			# This ain't fine-grained enough.  Narrow it down
			self.set_static( detailed_name, True )
			os_sequence[1] = detailed_name
	
		# Set the internal name
		self.set_static( 'os', os_sequence )
	
	def set_core( self ):
		'Find paths to a few basic core utilities'
		# TODO: These should probably be their own command objects for greater
		# flexibility.
		platform_hash = {
			'posix': {'delete': 'rm', 'copy': 'cp', 'move': 'mv'},
			'windows': {'delete': 'del', 'copy': 'copy', 'move': 'move'}
			}
		
		if not platform_hash.has_key( self['os'][0] ):
			raise Command.CommandError( self.name, 'Unsupported platform' )
		
		results = platform_hash[self['os'][0]]
		for program in results:
			self.set_static( program, self.env.find_program( results[program] ))
	
	def run( self ):
		'Check if this platform is supported'
		supported = []
		unsupported = []
		
		# See if any options are given
		try:
			supported = self['supported']
		except KeyError:
			pass
		try:
			unsupported = self['unsupported']
		except KeyError:
			pass
		
		# See if we have to check anything
		if not supported and not unsupported:
			return
		
		self.env.output.start( 'Checking platform...' )

		# If supported is given, go on a whitelist system
		os = self['os']
		if supported:
			if os[0] in supported or os[1] in supported:
				self.env.output.success( str( self ))
			else:
				self.env.output.error( 'unsupported' )
				
			return
		
		# Black-list system
		if os[0] in unsupported or os[1] in unsupported:
			self.env.output.error( 'unsupported' )
		else:
			self.env.output.success( str( self ))
				
	def __str__( self ):
		return r'/'.join( self['os'] )
