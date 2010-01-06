import sys
import re
import os
import os.path

import Command
import Make
import VarStore
import Command

class ConfigError( Exception ):
	pass

class NoSuchCommand( ConfigError ):
	def __init__( self, command ):
		self.command = command

class Output:
	# Thanks to mem (http://github.com/srp/mem/) for these escape codes
	SUCCESS = chr( 27 ) + '[32m'
	WARNING = chr( 27 ) + '[33m'
	ERROR   = chr( 27 ) + '[31m'
	RESET   = chr( 27 ) + '[0m'
	
	# TODO: We should be a *lot* smarter about this
	COLUMN_LEN = 60

	def __init__( self, path=None ):
		'Initialize an output system, with an optional log path.'
		if path:
			self.loghandle = open( path, 'w' )
		else:
			self.loghandle = None
	
	def start( self, task ):
		if not isinstance( task, basestring ):
			raise TypeError
		
		sys.stdout.write( task.ljust( Output.COLUMN_LEN ))
	
	def error( self, error ):
		message = ''.join( [Output.ERROR, error, Output.RESET] )
		print( message )
		self.log( message )
		
		# Quit
		sys.exit( 1 )
	
	def warning( self, warning ):		
		message = ''.join( [Output.WARNING, warning, Output.RESET] )
		print( message )
		self.log( message )

	def success( self, success ):
		message = ''.join( [Output.SUCCESS, success, Output.RESET] )
		print( message )
		self.log( message )
	
	def comment( self, msg ):
		print( msg )
		self.log( msg )
	
	def log( self, msg ):
		if self.loghandle:
			self.loghandle.write( msg + '\n' )


class Env:
	def __init__( self ):
		self.vars = VarStore.VarStore()
		self.output = Output()
		self.make = Make.Makefile()
		
		self.system_path = os.environ['PATH'].split( os.pathsep )
		
		# Cached list of commands so we can run them all without having to
		# search through all of the variables.
		self.commands = []
		
		self.var_regexp = re.compile( '\\$\\(([a-zA-Z_-]+)\\)' )
		
	def load_command( self, name, prefix ):
		'Return a command object of type name and with the supplied variable prefix'
		if self.vars.has_key( name ):
			# Don't have to do anything
			return
		
		# Import the command and create the instance
		try:
			# TODO: Make this a *LOT* cleaner!
			module = 'command_' + name
			full_module = 'commands.' + module
			try:
				command = getattr( getattr( __import__( full_module, Command ), module ), 'command' )
			except AttributeError:
				raise NoSuchCommand( name )
		except ImportError:
			# This is too broad of a catch
			raise NoSuchCommand( name )
		
		# Check the type
		if not issubclass( command, Command.Command ):
			raise NoSuchCommand( name )
		
		try:
			self.commands.append( command( self, prefix ))
		except Command.CommandError as e:
			self.output.error( str( e ))
			
		return self.commands[-1]
	
	def variables( self ):
		'Get a list of variables in this environment'
		return self.vars.keys()

	def has_variable( self, var ):
		return self.vars.has_key( var )
	
	def __getitem__( self, key ):
		value = self.vars[key]
		return value
	
	def __setitem__( self, key, value ):
		self.vars[key] = value
	
	def __len__( self ):
		return len( self.vars )

	def __iter__( self ):
		return iter( self.vars )

	def run_commands( self ):
		'Run all of the command objects that we have stored.'
		# New objects may be created in the execution process.  This is
		# undesirable, so let's create a copy of our current command list.
		commands = list( self.commands )
		for command in commands:
			try:
				command.run()
			except Command.CommandError as e:
				self.output.error( str( e ))
	
	def find_program( self, name ):
		'Find the path of a program on the system, also confirming that it exists.'
		for path in self.system_path:
			chosen_path = os.path.join( path, name )
			if os.access( chosen_path, os.X_OK ):
				return chosen_path
		
		return None