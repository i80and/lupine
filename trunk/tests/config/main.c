#include <stdio.h>
#include "config.h"

int main( int argc, char** argv )
{
	#ifdef HAVE_TAR_H
		printf( "Have tar\n" );
	#else
		printf( "Lack tar\n" );
	#endif

	#ifdef HAVE_FOO_H
		printf( "Have foo\n" );
	#else
		printf( "Lack foo\n" );
	#endif
	
	return 0;
}
