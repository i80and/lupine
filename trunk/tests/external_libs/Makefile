CC = /usr/bin/gcc

.PHONY: all clean
all: test

test: src/main.o
	gcc src/main.o -otest

src/main.o: src/main.c
	gcc src/main.c -osrc/main.o -c

clean: 
	/usr/bin/rm src/main.o
	/usr/bin/rm test

