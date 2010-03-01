CC = /usr/bin/gcc

.PHONY: all clean
all: basic

foo\ bar.o: foo\ bar.c foo.h
	gcc foo\ bar.c -c -ofoo\ bar.o

foo.o: foo.c
	gcc foo.c -c -ofoo.o

basic: foo\ bar.o foo.o
	gcc foo\ bar.o foo.o -obasic

clean: 
	/usr/bin/rm basic
	/usr/bin/rm foo\ bar.o
	/usr/bin/rm foo.o

