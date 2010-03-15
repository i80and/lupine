#include <stdio.h>
#include "config.h"

int main( int argc, char** argv )
{
	#ifdef MATH_H
		printf( "Have math\n" );
	#else
		printf( "Lack math\n" );
	#endif

	#ifdef HAVE_FOO_H
		printf( "Have foo\n" );
	#else
		printf( "Lack foo\n" );
	#endif
	
	return 0;
}
