import subprocess
import Command

class command( Command.Command ):
	name = 'pkgconfig'
	attributes = {'name': basestring,
					'required':bool
				}
	
	def __init__( self, env, var_name ):
		Command.Command.__init__( self, env, var_name )
		self.path = self.env.find_program( 'pkg-config' )
	
	def run( self ):
		'The actual execution stage.'
		name = self['name']
		self.set_child_command( 'c', 'compiler' )
		cmd = [self.path, '--libs', '--cflags', name]
		
		# Check if we've already found this library
		if self.has_variable( name ):
			self.set_instance( 'output', self[name] )
			return
		
		# See if we need to add the MSVC option.  UGLY.
		if self['compiler'].get_compiler() == 'msvc':
			cmd.append( '--msvc-syntax' )
		
		self.env.output.start( 'Checking for {0}...'.format( name ))
		process = subprocess.Popen( cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT )
		result = process.communicate()[0]
		code = process.returncode
		
		if code != 0:
			if self['required']:
				self.env.output.error( 'not found' )
			else:
				self.env.output.warning( 'not found' )
		else:
			self.env.output.success( 'found' )
		
		# Store our output
		self.set_static( name, result )
		self.set_instance( 'options', self[name] )
		
	def __nonzero__( self ):
		return not bool( subprocess.call( [self.path, '--exists', self['name']] ))
	
	def __str__( self ):
		return self.name
