import re
import os.path
import Command
import CCompilers

class NoCompilerFound( Command.CommandError ):
	def __str__( self ):
		if self.msg:
			return 'Cannot find C compiler: {0}'.format( self.msg )
		else:
			return 'Cannot find C compiler.'

class SourceNotFound( Command.CommandError ):
	pass

class command( Command.Command ):
	'''%ccompiler - Look for and represent an installed C compiler.
Valid options:
  * compilers - Ordering of preferred compilers
  * whitelist - List of exclusively-working compilers
  * blacklist - List of banned compilers
'''
	name = 'ccompiler'
	compiler_hash = {
		'posix': [CCompilers.clang, CCompilers.gcc],
		'default': [CCompilers.cc]
		}

	_dep_pat = re.compile( '(?:#include|#import) (<|")(.+)(?:>|")', re.M )
	
	def run( self ):
		'The actual execution stage.'
		self.setup()
	
	def setup( self ):
		'Find a working compiler and other such initial setup tasks'	
		# If we've already found which compiler we need, just instantiate it
		if self.has_variable( 'compiler' ):
			self.set_child_command( self['compiler'], 'compiler' )
			return
			
		self.set_child_command( 'platform', 'os' )
		
		# Look for an installed and supported compiler
		self.env.output.start( 'Looking for the {0} C compiler...'.format( self.reference_name ))
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

		if len( compilers ) == 0:
			raise NoCompilerFound( self.name, self.reference_name )

		# The compilers are sorted in order of decreasing preference; choose the first.
		compiler = compilers[0][0]
		self.env.output.success( compilers[0][1] )
		
		# Set up our Make macros
		self.env.make.add_macro( 'CC', compilers[0][1] )

		# Instantiate the compiler		
		self.set_instance( 'compiler', compiler() )

		# Store the path to the compiler
		self['compiler'].path = compilers[0][1]
			
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
				path = self.env.find_program( compiler.name )
				if path:
					compilers.append(( compiler, path ))
		
		return compilers

	def get_deps( self, path ):
		'Get a list of dependencies for the file pointed to by this path'
		# This is a very cruddy and naive algorithm based on regexps
		# TODO: Implement something more sophisticated!
		
		# This is our processing queue
		queue = [path]
		output = {}
		
		for dep in queue:
			output[dep] = None
			
			# Open the file we're checking out
			try:
				f = open( dep, 'r' )
			except IOError:
				raise SourceNotFound( self.name, 'Source file {0} not found'.format( dep ))
			# Look for the pattern
			potential_deps = self._dep_pat.findall( f.read())
			f.close()
					
			for potential_dep in potential_deps:
				# Don't allow duplicates
				if output.has_key( potential_dep[1] ):
					continue
					
				# Right now we only look at non-system headers	
				if potential_dep[0] == '"':
					queue.append( os.path.join( os.path.split( dep )[0], potential_dep[1] ))
		
		return output.keys()
		
	def config_header( self ):
		return self['compiler'].name
			
	def __str__( self ):
		return 'CCompiler'
