import subprocess
import Lib

class pkgconfig( Lib.Library ):
	'''pkgconfig - Represent a pkg-config library.
Valid options:
  * pkg - Name of the package to check for
  * required - Whether or not this library is required to exist
'''

	def __init__( self, env, compiler, pkg='', required=True ):
		'The actual execution stage.'
		self.env = env
		self.pkg = pkg
		self.path = self.env.find_program( 'pkg-config' )
	
		cmd = [self.path, '--libs', '--cflags', pkg]
		
		# See if we need to add the MSVC option.  Inflexible... >.>
		if compiler.compiler.name == 'msvc':
			cmd.append( '--msvc-syntax' )
		
		self.env.output.start( 'Checking for {0}...'.format( pkg ))
		process = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
		result = process.communicate()[0]
		code = process.returncode
		
		if code != 0:
			if required:
				self.env.output.error( 'not found' )
			else:
				self.env.output.warning( 'not found' )
		else:
			self.env.output.success( 'found' )
		
		# Store our output, cutting off the trailing newline
		Lib.Library.__init__( self, compiler, options=[result[0:-2]] )
		
	def __nonzero__( self ):
		return not bool( subprocess.call( [self.path, '--exists', pkg] ))
