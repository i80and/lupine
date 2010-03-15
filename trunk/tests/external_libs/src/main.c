#include <glib.h>
#include <ncurses.h>

int main( int argc, char** argv )
{
	GString* str = g_string_new( "Foo" );
	g_free( str );
	
	initscr();
	printw( "Test Success" );
	refresh();
	getch();
	endwin();

	return 0;
}
