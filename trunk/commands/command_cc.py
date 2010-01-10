import os
import os.path
import re
import subprocess
import Command
import command_c

class SourceNotFound( Command.CommandError ):
	pass

class command( Command.Command ):
	'Generic C compiler'
	name = 'cc'
	objcode_ext = '.o'
	shared_ext = '.so'
	program_ext = ''
	
	__dep_pat = re.compile( '(?:#include|#import) (<|")(.+)(?:>|")', re.M )
	
	def run( self ):
		'The actual execution stage.'
		# Create a platform information object to get some information
		self.set_child_command( 'platform', 'os' )
		
		# Create object code rules
		objects = []
		for srcfile in self['src']:
			if isinstance( srcfile, command_c.command ):
				# If we're linking to another C object, add its object code to our link list
				objects.extend( srcfile['output'] )
				continue
			
			objects.append( self.env.escape_whitespace( self.target_name( srcfile, self.objcode_ext )))
			
			target = objects[-1]
			command = self.create_make_command( srcfile, target, 'objcode' )
			deps = [self.env.escape_whitespace( dep ) for dep in self.get_deps( srcfile )]
			self.env.make.add_rule( target, deps, command )
			
			self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))

		# Now create the end product
		if self['type'] == 'objcode':
			# If object code is our target, quit now
			return
		elif self['type'] == 'program':
			# Create an executable
			target = self.env.escape_whitespace( self.target_name( self['target'], self.program_ext ))
			command = self.create_make_command( objects, target, self['type'] )
			self.env.make.add_rule( target, objects, command, default=True )
			
			self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))
		
	def create_make_command( self, src, target, type ):
		'Create a statement suitable for compiling source in a makefile'
		if isinstance( src, list ):
			src = ' '.join( src )	
		elif isinstance( src, str ):
			src = self.env.escape_whitespace( src )
			
		return '$(CC) {0} {1}'.format( src, self.get_cflags( target, type ))
		
	def get_cflags( self, target, type ):
		'Create a compile command.'
		cflags = []

		if type == 'program' or type == 'shared':
			if self['link']:
				cflags.append( self.link( self['link'], self['link_paths'] ))

		if target:
			if type == 'program':
				cflags.append( self.output_program( target ))
			elif type == 'objcode':
				cflags.append( self.output_objcode( target ))
			elif type == 'shared':
				cflags.append( self.output_shared( target ))
			else:
				return ''
		
		if self['debug']:
			cflags.append( self.debug())
		if self['optimize']:
			cflags.append( self.optimize( self['optimize'] ))
		if self['define']:
			cflags.append( self.set_defines( self['define'] ))
		if self['options']:
			cflags.append( self['options'] )
		
		return ' '.join( cflags )
	
	def output_program( self, dest ):
		return '-o {0}'.format( dest )
	
	def output_objcode( self, dest ):
		return '-c -o {0}'.format( dest )

	def output_shared( self, dest ):
		return '-shared -o {0}{1}'.format( dest, self.shared_ext )

	def link( self, targets, paths ):
		'Add link flags to link to targets searching within paths.'
		if paths:
			paths = ' '.join( ['-L{0}'.format( path ) for path in paths] )
		
		if targets:
			targets = ' '.join( ['-l{0}'.format( target ) for target in targets] )
		
		if targets and paths:
			return '{0} {1}'.format( paths, targets )
		elif targets:
			return targets
		else:
			return ''

	def optimize( self, level ):
		return ''

	def debug( self ):
		return ''

	def set_defines( self, assignments ):
		'Define a macro for this object.'
		# Assignments should be a list, each element being of form x=v
		return ' '.join( ['-D {0}'.format( self.env.escape( assignment, '"' )) for assignment in assignments])

	def target_name( self, name, ext ):
		'Give what the name of object code output is going to be.'
		return os.path.splitext( name )[0] + ext

	def get_deps( self, path ):
		'Get a list of dependencies for the file pointed to by this path'
		# This is a very cruddy and naive algorithm
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
			potential_deps = self.__dep_pat.findall( f.read())
			f.close()
					
			for potential_dep in potential_deps:
				# Don't allow duplicates
				if output.has_key( potential_dep[1] ):
					continue
					
				# Right now we only look at non-system headers	
				if potential_dep[0] == '"':
					queue.append( os.path.join( os.path.split( dep )[0], potential_dep[1] ))
		
		return output.keys()

	def test_lib( self, libname, path ):
		'Test to see if we can link to a given library'
		command = [self['path']]
		output_name = '__lupine_test_{0}'.format( libname )
		
		if not path:
			path = []
		
		command.extend( self.output_shared( output_name ).split( ' ' ))
		command.extend( self.link( libname, path ).split( ' ' ))
		result = subprocess.call( command, stderr=subprocess.PIPE )
		
		# Remove our temp output file
		try:
			os.remove( '{0}{1}'.format( output_name, self.shared_ext ))
		except OSError:
			pass
		
		# 0 indicates success, but is technically False.  Fix that
		return not bool( result )

	def get_objcode_output( self ):
		'Get the expected output filenames of this module'
		output = [self.env.escape_whitespace( self.target_name( src, self.objcode_ext ))
			for src in self['src'] if not isinstance( src, Command.Command )]
		
		self.set_instance( 'output', output )
		return output

	def __str__( self ):
		return 'cc'
