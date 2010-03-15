import re
import os.path

class config:
	'''config - Write out a config.h file.
Valid options:
  * output - The path to write this file out to.  If not given, defaults to ./config.h
  * options - A dictionary of associations.
'''
	OUTPUT_TEMPLATE = '''#ifndef __{0}_H__
#define __{0}_H__
{1}
#endif'''
	ASSIGNMENT = '#define {0} {1}'
	HEADER_ID_REGEXP = re.compile( '[^\w]*' )

	def __init__( self, env, config, output='config.h' ):
		# (Hopefully) uniquely identify this header
		header_id = os.path.splitext( os.path.basename( output ))[0]
		header_id = self.HEADER_ID_REGEXP.sub( '', header_id )
		
		defines = {}
		for option in config:
			setting = config[option]
			
			# If this resolves to false, just outright skip it.
			if not setting:
				continue
			
			if hasattr( setting, "config_header" ):
				setting = setting.config_header()
			else:
				setting = int( bool( setting ))
			
			# Force double-quotes
			if isinstance( setting, basestring ):
				setting = '"{0}"'.format( setting )
			
			defines[option] = setting
			
		contents = '\n'.join( [self.ASSIGNMENT.format( define, defines[define] )
			for define in defines] )
		
		# Write the header
		f = open( output, 'w' )
		f.write( self.OUTPUT_TEMPLATE.format( header_id, contents ))
		f.close()
