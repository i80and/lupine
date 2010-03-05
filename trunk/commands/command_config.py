import re
import os.path
import Command

class InvalidAssignmentPair( Command.CommandError ):
	def __init__( self, name ):
		self.name = name
	
	def __str__( self ):
		return 'Invalid assignment pairing in {0}'.format( self.name )

class command( Command.Command ):
	'''%config - Write out a config.h file.
Valid options:
  * output - The path to write this file out to.  If not given, defaults to ./config.h
  * options - A list of association pairs; [foo 5 bar 10] would set foo=5 and bar=10
'''
	OUTPUT_TEMPLATE = '''#ifndef __{0}_H__
#define __{0}_H__
{1}
#endif'''
	ASSIGNMENT = '#define {0} {1}'
	HEADER_ID_REGEXP = re.compile( '[^\w]*' )

	name = 'config'
	def run( self ):
		'The actual execution stage.'
		self.verify()
		
		# (Hopefully) uniquely identify this header
		header_id = os.path.splitext( os.path.basename( self['output'] ))[0]
		header_id = self.HEADER_ID_REGEXP.sub( '', header_id )
		
		# Body of the header
		if len( self['options'] ) % 2:
			raise InvalidAssignmentPair( self.reference_name )
		
		defines = {}
		i = -1
		for option in self['options']:
			i += 1
			if not i % 2:
				# Macro name
				name = option
			else:
				# Macro assignment
				# If this resolves to false, just outright skip it.
				if not option:
					continue
					
				if hasattr( option, "config_header" ):
					option = option.config_header()
				else:
					option = str( option )
				
				# Force double-quotes
				if isinstance( option, basestring ):
					option = '"{0}"'.format( option )
				
				defines[name] = option
			
		contents = '\n'.join( [self.ASSIGNMENT.format( define, defines[define] )
			for define in defines] )
		
		# Write the header
		f = open( self['output'], 'w' )
		f.write( self.OUTPUT_TEMPLATE.format( header_id, contents ))
		f.close()
	
	def verify( self ):
		'Verify options'
		if not self.has_variable( 'output' ):
			self['output'] = './config.h'
		
		if not self.has_variable( 'options' ):
			self['options'] = []
	
	def __str__( self ):
		return 'config'

