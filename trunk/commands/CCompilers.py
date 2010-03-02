import os
import os.path
import subprocess

class cc:
	'Generic compiler driver'
	name = 'cc'
	path = name
	
	def name_obj( self, name ):
		return '{0}.o'.format( os.path.splitext( name )[0] )

	def name_program( self, name ):
		return os.path.splitext( name )[0]
	
	def optimize( self, level ):
		return ''

	def command( self, src, target, linking, optimize, include_paths, libs,
				lib_paths, options ):
		'Generic method to return a command'
		src = ' '.join( src )
		command = [self.name, src, '-o{0}'.format( target )]
		
		# Optional additions
		if linking:
			command.append( linking )
		
		optimize = self.optimize( optimize )
		if optimize:
			command.append( optimize )
		
		if include_paths:
			command.append( include_paths )

		if lib_paths:
			command.append( lib_paths )
			
		if libs:
			command.append( libs )
		
		if options:
			command.append( options )
			
		return ' '.join( command )

	def output_objcode( self, src, optimize, include_paths, options ):
		'Create a command to output object code.'
		output = self.name_obj( src )
		
		include_paths = ['-I{0}'.format( path ) for path in include_paths]
		include_paths = ' '.join( include_paths )

		return self.command( [src], output, '-c', optimize, include_paths, [], [], options )

	def output_program( self, src, target, optimize, libs, lib_paths, options ):
		'Create a command to output a program.'
		libs = ['-l{0}'.format( lib ) for lib in libs]
		libs = ' '.join( libs )
		lib_paths = ['-L{0}'.format( path ) for path in lib_paths]
		lib_paths = ' '.join( lib_paths )
		
		return self.command( src, target, '', optimize, [], libs, lib_paths, options )

	def output_shared( self, src, target, optimize, libs, lib_paths, options ):
		'Create a command to output a library.'
		# TODO: This is cheap.  I think we should use libtool or something?
		options += ' -shared -fPIC'
		return self.output_program( src, target, optimize, libs, lib_paths, options )

	def test_lib( self, libname, paths ):
		'Test to see if we can link to a given library.'
		output_name = '__lupine_test_{0}'.format( libname )
		
		if not paths:
			paths = []
		
		command = self.output_shared( [], output_name, None, [libname], paths, '' )
		command = command.split()
		result = subprocess.call( command, stderr=subprocess.PIPE )
		
		# Remove our temp output file
		try:
			os.remove( self.name_program( output_name ))
		except OSError:
			pass
		
		# 0 indicates success, but is technically False.  Fix that
		return not bool( result )
	
	def test_header( self, header, paths ):
		'Test to see if we can include a given header.'
		src_name = '__lupine_test_{0}.c'.format( header )
		src = open( src_name, 'w' )
		src.write( '#include <{0}>\nint main(int argc,char** argv){{return 0;}}'.format( header ))
		src.close()
		
		if not paths:
			paths = []
		
		command = self.output_objcode( src_name, None, paths, '' )
		command = command.split()
		result = subprocess.call( command, stderr=subprocess.PIPE )
		
		# Remove our temp output file
		try:
			os.remove( src_name )
			os.remove( self.name_obj( src_name ))
		except OSError:
			pass
		
		# 0 indicates success, but is technically False.  Fix that
		return not bool( result )

class gcc( cc ):
	'GCC compiler driver'
	name = 'gcc'
	
	def optimize( self, level ):
		if level == 'debug':
			return '-O0 -g -Wall'
		elif level == 0:
			return '-O1'
		elif level == 1 or level == True:
			return '-O2 -s'
		elif level == 2:
			return '-O3 -s'
		else:
			return ''

class clang( gcc ):
	'Clang compiler driver'
	name = 'clang'
