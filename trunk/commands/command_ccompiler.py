import re
import os.path
import glob

import LinkedTarget
import Lib
import CCompilers

class CompilerError( Exception ):
	def __init__( self, msg='' ):
		self.msg = msg

class SourceNotFound( CompilerError ):
	def __str__( self ):
		return 'Source file not found: {0}'.format( self.msg )

class ccompiler:
	'''ccompiler - Look for and represent an installed C compiler.
Valid options:
  * compilers - Ordering of preferred compilers
  * whitelist - List of exclusively-working compilers
  * blacklist - List of banned compilers
'''
	compiler_hash = {
		'posix': [CCompilers.clang, CCompilers.gcc],
		'default': [CCompilers.cc]
		}

	_dep_pat = re.compile( '(?:#include|#import) (<|")(.+)(?:>|")', re.M )
	
	def __init__( self, env, compilers=[], whitelist=[], blacklist=[] ):
		'The actual execution stage.'
		self.env = env
		self.setup( compilers, whitelist, blacklist )
	
	def setup( self, compilers, whitelist, blacklist ):
		'Find a working compiler and other such initial setup tasks'	
		self.os = self.env.load( 'platform' )
		self.optimize = 1
		
		# Look for an installed and supported compiler
		self.env.output.start( 'Looking for a C compiler...' )
		compilers = self.find_compilers()
		
		if compilers:
			# Re-sort the compilers based on a user-provided preference
			# TODO: Make this sorting process cleaner.  This is just ugly.
			new_compilers = []
			
			# Add the preferred
			for preferred_compiler in compilers:
				for compiler in compilers:
					if compiler[0].name == preferred_compiler:
						new_compilers.append( compiler )
						break

			# Add the rest
			for compiler in compilers:
				if not compiler in new_compilers:
					new_compilers.append( compiler )
			
			compilers = new_compilers
		
		if whitelist:
			# Remove any compilers not in the whitelist
			compilers = [compiler for compiler in compilers if compiler[0].name in whitelist]
			
		if blacklist:	
			# Remove any compilers in the blacklist
			compilers = [compiler for compiler in compilers if not compiler[0].name in blacklist]

		if len( compilers ) == 0:
			self.env.output.error( 'No compiler found' )

		# The compilers are sorted in order of decreasing preference; choose the first.
		compiler = compilers[0][0]
		self.env.output.success( compilers[0][1] )
		
		self.compiler = compiler()		

		# Store the path to the compiler
		self.compiler.path = compilers[0][1]
			
	def find_compilers( self ):
		'Find a supported compiler.'
		os = self.os.os
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
				self.env.output.error( 'Source file {0} not found'.format( dep ))

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

	def program( self, target, src, **args ):
		'Return a target describing an executable program'
		if not isinstance( target, basestring ):
			raise TypeError, target
		
		target = self.compiler.name_program( target )
		linked = LinkedTarget.LinkedTarget( self.env, src, target, self, False, **args )
		self.env[target] = linked
		return linked
	
	def shared( self, target, src, **args ):
		'Return a target describing a shared library'
		if not isinstance( target, basestring ):
			raise TypeError, target
		
		target = self.compiler.name_program( target )
		linked = LinkedTarget.LinkedTarget( self.env, src, target, self, True, **args )
		self.env[target] = linked
		return linked

	def lib( self, name, required=True, **args ):
		self.env.output.start( 'Checking for {0}'.format( name ))
		lib = Lib.Library(  self, **args )
		if lib:
			self.env.output.success( 'found' )
		else:
			if required:
				self.env.output.error( 'not found' )
			else:
				self.env.output.warning( 'not found' )

		self.env[name] = lib
		return lib

	def config_header( self ):
		return self.compiler.name

	def __nonzero__( self ):
		return bool( self.compiler )
