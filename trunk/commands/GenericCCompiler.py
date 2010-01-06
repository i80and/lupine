import re
import os

import CDriverExceptions
import pathutils

class GenericCompiler:
	name = 'cc'
	option_optimize = ''
	option_debug = ''
	option_objcode = '-c'
	option_objcode_output = '-o'
	option_output = '-o'
	option_define = '-D'

	option_include = '-I'
	option_link = '-l'
	
	option_shared = '-shared'
	
	option_objcode_ext = '.o'
	option_program_ext = ''
	
	# Parsing stuff
	__dep_pat = re.compile( '(?:#include|#import) (<|")(.+)(?:>|")', re.M )
	
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
				raise CDriverExceptions.SourceNotFound( 'Source file {0} not found'.format( dep ))
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

	def target_objcode( self, name ):
		'Give what the name of object code output is going to be.'
		return os.path.splitext( name )[0] + self.option_objcode_ext
	
	def target_program( self, name ):
		'Give what the name of object code output is going to be.'
		return os.path.splitext( name )[0] + self.option_program_ext
	
	def get_command( self, type, target, src ):
		cc = '$(CC)'
		
		if type == 'objcode':
			cflags = [self.option_objcode, self.option_objcode_output, target]
		elif type == 'program':
			cflags = [self.option_output, target]
		elif type == 'shared':
			pass
		elif type == 'static':
			pass
		else:
			# This should never happen, but fail gracefully just in case
			return None
	
		# Add optional additional flags
		if self.optimize:
			cflags.append( self.option_optimize )
		
		if self.debug:
			cflags.append( self.option_debug )
		
		cflags.append( self.options )
		cflags = ' '.join( cflags )

		return ' '.join( [cc, src, cflags ] )
	
	def rule( self, make, rm ):
		'Create the make rules'
		# A list of generated object code for this module
		module_objcode = []
		
		# Create our rules
		for src in self.src:
			deps = [pathutils.escape( srcfile ) for srcfile in self.get_deps( src )]
			target = pathutils.escape( self.target_objcode( src ))
			commands = self.get_command( 'objcode', target, pathutils.escape( src ))
			
			# Create the actual compile rule
			make.add_rule( target, deps, commands )	
			module_objcode.append( target )
			
			# EWWW.  In a perfect world, all the C compiler drivers would be command
			# objects of their own, but they aren't so this is how we're doing things
			# right now.  Cover your eyes, children.
			# Set up the clean target
			make.add_clean( '{0} {1}'.format( rm, target ))
			
		# Write rule for the main module
		if self.type == 'program':
			module_commands = self.get_command( self.type,
				self.target_program( self.target ), ' '.join( module_objcode ))
			make.add_rule( self.target, module_objcode, module_commands, default=True )
			make.add_clean( '{0} {1}'.format( rm, self.target ))
