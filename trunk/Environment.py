import sys
import re
import os
import os.path

import Make

class ConfigError( Exception ):
	pass

class NoSuchCommand( ConfigError ):
	def __init__( self, command ):
		self.command = command

class Output:
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
		
		# Tasks can have sub-tasks.  As such, we need to be able to queue
		# several levels of tasks, and print them off in the correct order
		# once all of them have been ended
		self.queued_logs = []
		self.results = []
	
	def start( self, task ):
		'Print that a task is beginning'
		message = task.ljust( self.COLUMN_LEN )
		self.queued_logs.insert( 0, message.ljust( self.COLUMN_LEN ))
		
		# Print a first-tier task immediately to keep the user informed
		if len( self.queued_logs ) == 1:
			sys.stdout.write( self.queued_logs[-1].ljust( self.COLUMN_LEN ))
	
	def finish( self, message ):
		'Finish the most recently-opened task'
		self.results.append( message )
		
		# If all tasks have been completed, print them all
		if len( self.queued_logs ) == len( self.results ):
			# The chronologically first task has already been printed; blank it
			self.queued_logs[-1] = ''
			
			while( self.queued_logs ):
				sys.stdout.write( self.queued_logs.pop())
				print( self.results.pop())
		elif len( self.results ) > len( self.queued_logs ):
			# Disassociated result
			print( self.results.pop())
	
	def error( self, error ):
		'Print that a critical task failed, and exit'
		message = ''.join( [Output.ERROR, error, Output.RESET] )
		self.finish( message )
		self.log( message )

		# Quit
		sys.exit( 1 )
	
	def warning( self, warning ):
		'Print that a task failed'
		message = ''.join( [Output.WARNING, warning, Output.RESET] )
		self.finish( message )
		self.log( message )

	def success( self, success ):
		'Print that a task succeeded'
		message = ''.join( [Output.SUCCESS, success, Output.RESET] )
		self.finish( message )
		self.log( message )
	
	def comment( self, msg, error=False ):
		if error:
			print( ''.join( [Output.ERROR, msg, Output.RESET] ))
			sys.exit( 1 )
		else:
			print( msg )
		self.log( msg )
	
	def log( self, msg ):
		'Log to a file'
		if self.loghandle:
			self.loghandle.write( msg + '\n' )


class Env:
	def __init__( self ):
		self.targets = {}
		self.output = Output()
		self.make = Make.Makefile()
		self.args = {}
		
		self.system_path = os.environ['PATH'].split( os.pathsep )
		
		self.space_regexp = re.compile( '\s' )

	def has_command( self, name ):
		'Check if the given command exists'
		try:
			__import__( 'commands.command_{0}'.format( name ))
		except ImportError:
			return False
		
		return True

	def load( self, name, **args ):
		'Return a command object of type name'
		# Import the command and create the instance
		try:
			module = 'command_' + name
			full_module = 'commands.' + module
			try:
				command = getattr( getattr( __import__( full_module ), module ), name )
			except AttributeError:
				raise NoSuchCommand( name )
		except ImportError as e:
			# This is too broad of a catch
			raise NoSuchCommand( name )
		
		return command( self, **args )
	
	def find_program( self, name ):
		'Find the path of a program on the system, also confirming that it exists.'
		for path in self.system_path:
			chosen_path = os.path.join( path, name )
			if os.access( chosen_path, os.X_OK ):
				return chosen_path
		
		return None
		
	def escape_whitespace( self, str ):
		'Escape whitespace in a string.'
		return self.space_regexp.sub(( lambda s: '\\' + s.group()), str )
	
	def escape( self, str, char ):
		'Escape instance of char in str.'
		escaped = '\\' + char
		return str.replace( char, escaped )
	
	def __getitem__( self, key ):
		return self.targets[key]

	def __setitem__( self, key, value ):
		self.targets[key] = value
