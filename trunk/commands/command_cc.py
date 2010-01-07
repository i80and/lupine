import os.path
import re
import Command

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
			target = self.env.escape_whitespace( self.target_name( srcfile, self.objcode_ext ))
			command = self.output( self.env.escape_whitespace( srcfile ), target, 'objcode' )
			deps = [self.env.escape_whitespace( dep ) for dep in self.get_deps( srcfile )]
			self.env.make.add_rule( target, deps, command )
			
			objects.append( target )
			self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))
		
		# Now create the end product
		if self['type'] == 'program':
			target = self.env.escape_whitespace( self.target_name( self['target'], self.program_ext ))
			command = self.output( objects, target, self['type'] )
			self.env.make.add_rule( target, objects, command, default=True )
			
			self.env.make.add_clean( '{0} {1}'.format( self['os']['delete'], target ))
		
	def output( self, src, target, type ):
		'Create a compile command.'
		cflags = []
				
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
			#print self['define']
		if self['options']:
			cflags.append( self['options'] )
		
		cflags = ' '.join( cflags )
		if isinstance( src, list ):
			src = ' '.join( src )
		
		return '$(CC) {0} {1}'.format( src, cflags )
	
	def output_program( self, dest ):
		return '-o {0}'.format( dest )
	
	def output_objcode( self, dest ):
		return '-c -o {0}'.format( dest )

	def output_shared( self, dest ):
		return '-shared -o {0}{1}'.format( dest, self.shared_ext )

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


	def __str__( self ):
		return 'cc'
