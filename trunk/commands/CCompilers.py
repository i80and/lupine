import GenericCCompiler

# Needs work
class msvc( GenericCCompiler.GenericCompiler ):
	name = 'cl'
	option_optimize = '/Ox'
	option_debug = '/Wall'
	option_objcode = '/c'
	option_objcode_output = '/Fo'
	option_output = '/LINK /OUT:'
	option_define = '/D'
	
	option_include = '/I'
	option_link = '/LINK /LIBPATH:'
	
	option_shared = '/LD'

	option_objcode_ext = '.obj'
	option_program_ext = '.exe.'

class tinycc( GenericCCompiler.GenericCompiler ):
	name = 'tcc'
	option_debug = '-b -Wall'

class gcc( GenericCCompiler.GenericCompiler ):
	name = 'gcc'
	option_optimize = '-O2'
	option_debug = '-g -Wall'

class clang( gcc ):
	name = 'clang'
