import os.path

import Command

class NoSourceError( Command.CommandError ):
	pass

class InvalidCompileTypeError( Command.CommandError ):
	pass

class command( Command.Command ):
	compiler_hash = {
		'posix': ['clang', 'gcc'],
		'default': ['cc']
		}
		
	name = 'c'

	def run( self ):
		'The actual execution stage.'
		if not self.has_variable( 'compiler' ):
			self.setup()
		
		self.set_child_command( self['compiler'], 'compiler' )
		compiler = self['compiler']

		# Set up our base directory
		if self.has_variable( 'basedir' ):
			basedir = self['basedir']
		else:
			basedir = './'
		
		# See if any special options are specified for this compiler
		if self.has_variable( compiler.name ):
			options = self[compiler.name]
		else:
			options = ''
		
		# Find our output target, or just get our variable name if none is specified
		if self.has_variable( 'target' ):
			target = self['target']
		else:
			target = self.reference_name

		# Debug overrides optimization
		debug = self['debug']
		optimize = False
		if not debug and self['optimize']:
			optimize = self['optimize']

		if self.has_variable( 'type' ):
			type = self['type']
		else:
			raise Command.CommandError( self.name, 'No compile type specified in ' + self.reference_name )
					
		if self.has_variable( 'src' ):		
			src = [os.path.join( basedir, srcfile ) for srcfile in self['src']]
		else:
			raise NoSourceError( self.name, 'No source specified in ' + self.reference_name )
		
		
		# Make sure our type is OK
		if not type in ['program', 'shared']:
			raise InvalidCompileTypeError( self.name, 'Invalid compile type specified for ' + self.reference_name )

		compiler.set_instance( 'options', options )
		compiler.set_instance( 'target', target )
		compiler.set_instance( 'optimize', optimize )
		compiler.set_instance( 'type', type )
		compiler.set_instance( 'src', src )

		# Now just create our make rules
		try:
			compiler.run()
		except Command.CommandError as e:
			self.env.output.error( e.msg )
		
	def setup( self ):
		'Find a working compiler and other such initial setup tasks'	
		self.set_child_command( 'platform', 'os' )
		
		# Look for an installed and supported compiler
		self.env.output.start( 'Looking for a C compiler...' )
		compilers = self.find_compilers()
		
		if self.has_variable( 'compilers' ):
			# Re-sort the compilers based on a user-provided preference
			# TODO: Make this sorting process cleaner.  This is just ugly.
			preferred = self['compilers']
			new_compilers = []
			
			# Add the preferred
			for preferred_compiler in preferred:
				for compiler in compilers:
					if compiler[0].name == preferred_compiler:
						new_compilers.append( compiler )
						break

			# Add the rest
			for compiler in compilers:
				if not compiler in new_compilers:
					new_compilers.append( compiler )
			
			compilers = new_compilers
		
		if self.has_variable( 'whitelist' ):
			# Remove any compilers not in the whitelist
			whitelist = self['whitelist']
			compilers = [compiler for compiler in compilers if compiler[0].name in whitelist]
				
		if self.has_variable( 'blacklist' ):
			# Remove any compilers in the blacklist
			blacklist = self['blacklist']
			compilers = [compiler for compiler in compilers if not compiler[0].name in blacklist]

		# The compilers are sorted in order of decreasing preference; choose the first.
		compiler = compilers[0][0]
		self.env.output.success( compilers[0][1] )
		
		# Set up our Make macros
		self.env.make.add_macro( 'CC', compilers[0][1] )
		
		# Store our compiler choice for other instances
		self.set_static( 'compiler', compiler )
	
	def find_compilers( self ):
		'Find a supported compiler.'
		os = self['os']['os']
		available_compilers = []
		
		if os[1]:
			# This is a general platform that we can check for specific brands with
			# Try to find a compiler for this specific platform
			available_compilers.extend( self.check_compilers( os[1] ))
		
		# Now check for generally-supported compilers
		available_compilers.extend( self.check_compilers( os[0] ))
		
		# Now check for catch-all choices
		available_compilers.extend( self.check_compilers( 'default' ))
		
		return available_compilers
		
	def check_compilers( self, platform ):
		'Check for a available compilers supporting the given platform'
		compilers = []
		
		if self.compiler_hash.has_key( platform ):
			for compiler in self.compiler_hash[platform]:
				path = self.env.find_program( compiler )
				if path:
					compilers.append(( compiler, path ))
		
		return compilers
					
	def __str__( self ):
		return 'Command({0} {1})'.format( self['src'], self['basedir'] )
