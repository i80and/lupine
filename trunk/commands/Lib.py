class Library:
	def __init__( self, compiler, libs=[], headers=[], libpaths=[],
					headerpaths=[], options=[] ):
		self.libs = libs
		self.headers = headers
		self.libpaths = libpaths
		self.headerpaths = headerpaths
		self.options = options
		
		self.compiler = compiler

		# Store whether or not all aspects of this library exist
		self.result = self.check_libs()
		if self.result:
			self.result = self.check_headers()

	def check_libs( self ):
		'Check if we can link to the given libraries'
		for lib in self.libs:
			if not self.compiler.compiler.test_lib( lib, self.libpaths ):
				return False
		
		return True
	
	def check_headers( self ):
		'Check if we can include the given libraries'
		for header in self.headers:
			if not self.compiler.compiler.test_header( header, self.headerpaths ):
				return False
		
		return True

	def __nonzero__( self ):
		return self.result
