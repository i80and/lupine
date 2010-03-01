CC = /usr/bin/gcc

.PHONY: all clean
all: test

main.o: os.h main.c
	gcc main.c -c -omain.o

test: posix.o main.o
	gcc posix.o main.o -otest

posix.o: posix.c
	gcc posix.c -c -oposix.o

clean: 
	/usr/bin/rm posix.o
	/usr/bin/rm main.o
	/usr/bin/rm test

