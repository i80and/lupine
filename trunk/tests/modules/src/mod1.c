#include <stdio.h>
#include "mod2.h"
#include "utils.h"

char* mod1()
{
	return "mod1";
}

int main( int argc, char** argv )
{
	printf( "%s %s %d\n", mod1(), mod2(), meaning());
	
	return 0;
}
