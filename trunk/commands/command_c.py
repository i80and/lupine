import os.path
import command_link
import Command
import glob

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
	attributes = {'basedir':basestring,
					'type':basestring,
					'src':list,
					'define':list,
					'link':list,
					'optimize':float,
					'debug':bool,
					'target':basestring,
					'compilers':list,
					'whitelist':list,
					'blacklist':list
				}

	def run( self ):
		'The actual execution stage.'
		self.setup()
		self.set_options()		
		compiler = self['compiler']
	
		# Check for required options
		if not compiler['src']:
			raise NoSourceError( self.name, 'No source specified in ' + self.reference_name )

		if not compiler['type']:
			raise Command.CommandError( self.name, 'No compile type specified in ' + self.reference_name )
	
		# Now just create our make rules
		try:
			compiler.run()
		except Command.CommandError as e:
			self.env.output.comment( e.msg, True )

	def set_options( self ):
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

		# Set up target type			
		if self.has_variable( 'type' ):
			compile_type = self['type']
		else:
			compile_type = None

		# Make sure our type is OK
		if not compile_type in ['program', 'shared', 'objcode']:
			raise InvalidCompileTypeError( self.name, 'Invalid compile type specified for ' + self.reference_name )
		
		if self.has_variable( 'src' ):
			# Apply the basedir and glob wildcards
			src = []
			for srcfile in self['src']:
				if isinstance( srcfile, basestring ):
					src.extend( glob.glob( os.path.join( basedir, srcfile )))
				else:
					src.append( srcfile )
			self.set_instance( 'src', src )
		else:
			src = []
		
				
		# Add link targets
		link = []
		link_paths = []
		if self['link']:
			for lib in self['link']:
				if isinstance( lib, basestring ):
					# Create a link object
					link_var_name = 'link_{0}'.format( lib )
					self.set_child_command( 'link', link_var_name )
					self[link_var_name].set_instance( 'name', lib )
					self[link_var_name].run()
					link.append( lib )
				
				if isinstance( lib, command_link.command ):
					# A link command object is given; it's already been tested
					# for, so just grab the path and name
					link.append( lib['name'] )
					link_paths.append( lib['path'] )
					
		compiler.set_instance( 'options', options )
		compiler.set_instance( 'target', target )
		compiler.set_instance( 'optimize', optimize )
		compiler.set_instance( 'type', compile_type )
		compiler.set_instance( 'src', src )
		#compiler.set_instance( 'include_paths', include_paths )
		compiler.set_instance( 'define', self['define'] )
		compiler.set_instance( 'link', link )
		compiler.set_instance( 'link_paths', link_paths )
	
		output = compiler.get_objcode_output()
		self.set_instance( 'output', output )
	
	def setup( self ):
		'Find a working compiler and other such initial setup tasks'	
		# If we've already found which compiler we need, just instantiate it
		if self.has_variable( 'compiler' ):
			self.set_child_command( self['compiler'], 'compiler' )
			return
			
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
		
		# Store our compiler choice for other instances, and instantiate the compiler
		# for this object
		self.set_static( 'compiler', compiler )
		self.set_child_command( self['compiler'], 'compiler' )


		# Store the path to the compiler
		self['compiler'].set_static( 'path', compilers[0][1] )
			
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

	def test_lib( self, libname, path ):
		'Test to see if we can link to a given library'
		self.setup()
		return self['compiler'].test_lib( libname, path )

	def __str__( self ):
		return 'Command({0} {1})'.format( self['src'], self['basedir'] )
