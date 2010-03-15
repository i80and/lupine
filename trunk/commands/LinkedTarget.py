import glob
import Lib
import Target

class LinkedTarget( Target.Target ):
	def __init__( self, env, src, target, compiler, shared, libs=[], options=[], optimize=[] ):

		self.src = src
		self.optimize = optimize
		
		self.env = env
		self.compiler = compiler
		self.target = target
		
		self.os = self.env.load( 'platform' )
		
		self._generic( shared, libs, options )

	def _generic( self, shared, libs=[], options=[] ):
		# Add linking data
		libsearch = []
		headersearch = []
		link_goals = []
		for lib in libs:
			if isinstance( lib, Lib.Library ):
				link_goals.extend( lib.libs )
				libsearch.extend( lib.libpaths )
				headersearch.extend( lib.headerpaths )
				options.extend( lib.options )
		
		# Fill in wildcards in our source
		newsrc = []
		for srcfile in self.src:
			newsrc.extend( glob.glob( srcfile ))
		
		# Create Make targets to create our object code
		outputs = []
		for srcfile in newsrc:
			outputs.extend( self._compile( srcfile, headersearch, False, options ))
		
		# Link all of our object code
		compile = self.compiler.compiler.output_program
		if shared:
			compile = self.compiler.compiler.output_shared
		self._link( outputs, link_goals, libsearch, options, compile )

	def _compile( self, srcfile, headersearch, shared, options ):
		'Generate object code from our source files'
		objects = []

		# Prepare our source
		target = self.env.escape_whitespace( self.compiler.compiler.name_obj( srcfile ))
		objects.append( target )
		escaped_src = self.env.escape_whitespace( srcfile )
		
		# Compile our source
		command = self.compiler.compiler.output_objcode( escaped_src, self.optimize, headersearch, shared, options )
		deps = [self.env.escape_whitespace( dep ) for dep in self.compiler.get_deps( srcfile )]
		self.env.make.add_rule( target, deps, command )
		
		# Make sure we can clean up after ourselves
		self.env.make.add_clean( '{0} {1}'.format( self.os.delete, target ))

		return objects
	
	def _link( self, objects, libs, libsearch, options, compile ):
		'Generate a binary from our object code'
		# Create our make command
		self.target = self.env.escape_whitespace( self.target )
		
		# Link all of our object code
		command = compile( objects, self.target, self.optimize, libs, libsearch, options )
		
		self.env.make.add_rule( self.target, objects, command, default=True )
		self.env.make.add_clean( '{0} {1}'.format( self.os.delete, self.target ))

