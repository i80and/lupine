#include <ncurses.h>

int main( int argc, char** argv )
{
	initscr();
	printw( "Test Success" );
	refresh();
	getch();
	endwin();

	return 0;
}
