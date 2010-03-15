class Rule:
	def __init__( self, target, deps, commands ):
		# Escape spaces in the target and dependency names
		self.target = target
		self.deps = deps
		self.commands = commands
		
	def __str__( self ):
		rule = []
		rule.append( '{0}: {1}'.format( self.target, ' '.join( self.deps )))
		for command in self.commands:
			rule.append( '\t' + command )
		
		rule.append( '\n' )
		return '\n'.join( rule )

class Makefile:
	header = '.PHONY: {0}\nall: {1}\n\n'
	
	def __init__( self ):
		self.phony = ['all', 'clean']
		self.clean = {}
		self.rules = {}
		self.default = []
		self.macros = {}

	def add_clean( self, command ):
		'Add a command to the clean target.'
		# Use a dictionary to avoid duplicates
		self.clean[command] = 1

	def add_macro( self, name, command ):
		'Add a macro definition to the start of the makefile'
		self.macros[name] = command

	def add_rule( self, target, deps, commands, phony=False, default=False ):
		'Add a rule to the makefile.'
		# If commands isn't a list, make it one
		if not isinstance( commands, list ):
			commands = [commands]
		
		# Avoid duplicates
		if target in self.rules:
			return
		
		rule = Rule( target, deps, commands )
		self.rules[target] = ( rule )
		
		# Add a phony marker if needed
		if phony:
			self.phony.append( target )
		
		# Should this be built as part of the standard build?
		if default:
			self.default.append( target )
			
	def write( self, path='Makefile' ):
		'Write out the described makefile'
		f = open( path, 'w' )
		
		# Set up our macros
		for macro in self.macros:
			macro_str = '{0} = {1}\n'.format( macro, self.macros[macro] )
			f.write( macro_str )

		# Newline to seperate macros from rules
		f.write( '\n' )
		
		# Add our phonies
		f.write( self.header.format( ' '.join( self.phony ), ' '.join( self.default )))

		# Set up our rules
		for rule in self.rules:
			rule_str = str( self.rules[rule] )
			f.write( rule_str )
		
		# Add our clean rule
		#f.write( str( Rule( 'clean', self.default, self.clean )))
		f.write( str( Rule( 'clean', [], self.clean.keys() )))
		
		f.close()
