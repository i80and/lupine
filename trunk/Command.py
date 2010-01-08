import VarStore

class CommandError( Exception ):
	def __init__( self, command, msg='' ):
		self.msg = msg
		self.command = command
	
	def __str__( self ):
		if self.msg:
			return 'Error in {0} command: {1}'.format( self.command, self.msg )
		else:
			return 'Error in {0} command.'.format( self.command )

class CommandMissingOption( CommandError ):
	def __str__( self ):
		if self.msg:
			return 'Missing required option in {0}: {1}'.format( self.command, self.msg )
		else:
			return 'Missing required option in {0} command.'.format( self.command )

class Command:
	'Abstract class representing a command object.'
	name = None
	
	def __init__( self, env, var_name ):
		self.reference_name = var_name
		self.add_env( env )
			
	def add_env( self, env ):
		self.env = env
	
	def run( self ):
		'The actual execution stage.'
		pass
	
	def set_static( self, name, value ):
		'Add a command-level variable'
		self.env.vars.set_var( self.name, name, value )
	
	def set_instance( self, name, value ):
		'Add an instance-level variable'
		self.env.vars.set_var( self.reference_name, name, value )
		
	def set_child_command( self, command_name, var_name ):
		'Store a command object inside this command object.'
		prefix = '{0}.{1}'.format( self.reference_name, var_name )
		self.set_instance( var_name, self.env.load_command( command_name, prefix ))
		
	def has_variable( self, var ):
		'See if this command object has a given variable.'
		instance_name = self.env.vars.var_name( self.reference_name, var )
		static_name = self.env.vars.var_name( self.name, var )

		return self.env.has_variable( instance_name ) or self.env.has_variable( static_name )
		
	def eval( self ):
		'Evaluate whether this command object is true or false.  Should be overridden.'
		return True
	
	def __getitem__( self, key ):
		instance_name = self.env.vars.var_name( self.reference_name, key )
		static_name = self.env.vars.var_name( self.name, key )
		
		if self.env.has_variable( instance_name ):
			# First check if we have an instance variable for this key			
			value = self.env[instance_name]
		elif self.env.has_variable( static_name ):
			# Then check if this command has a static variable
			value = self.env[static_name]
		else:
			return None
			#raise KeyError, key
		
		return value

	def __str__( self ):
		result = {}
		for element in self.instance:
			result[element] = self[element]
		return str( result )
