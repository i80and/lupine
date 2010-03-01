CC = /usr/bin/gcc

.PHONY: all clean
all: mod

src/mod2.o: src/mod2.c
	gcc src/mod2.c -c -osrc/mod2.o

src/utils.o: src/utils.c
	gcc src/utils.c -c -osrc/utils.o

mod: src/mod1.o src/mod2.o src/utils.o
	gcc src/mod1.o src/mod2.o src/utils.o -omod

src/mod1.o: src/mod1.c src/utils.h src/mod2.h
	gcc src/mod1.c -c -osrc/mod1.o

clean: 
	/usr/bin/rm src/utils.o
	/usr/bin/rm src/mod1.o
	/usr/bin/rm mod
	/usr/bin/rm src/mod2.o

