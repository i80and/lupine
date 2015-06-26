If any part of this document is wrong, out of date, or just suboptimal, please file a bug report!

# ccompiler #
A command object representing a C compiler.
The currently supported compilers are:
  * [clang](http://clang.llvm.org/)
  * [gcc](http://gcc.gnu.org/)
  * cc - A simple fallback mostly the same as gcc, but with some features such as optimization switched off.
Eventually, [TinyCC](http://bellard.org/tcc/) and [Microsoft Visual Studio C++](http://msdn.microsoft.com/en-us/visualc/default.aspx) will be added.

## Options ##
  * compilers
    * A list of compilers, listed in order of decreasing preference.  Any compiler listed here will be given preference over any not listed.
  * whitelist
    * A whitelist of compilers; any compiler not on this list will be rejected.
  * blacklist
    * A blacklist of compilers; any compiler on this list will be rejected.
## Sub-object Constructors ##
  * program( target, src, libs=[.md](.md), options=[.md](.md), optimize=1 )
    * Create an executable program target.
  * shared( target, src, libs=[.md](.md), options=[.md](.md), optimize=1 )
    * Create a shared library.
  * lib( name, libs=[.md](.md), headers=[.md](.md), libpaths=[.md](.md), headerpaths=[.md](.md), options=[.md](.md), required=True )
    * Create a Library object, checking if the libs and headers can be found, suitable for passing to program() and shared().
## Examples ##
```
compiler = env.load( 'ccompiler' )
basic = compiler.program( 'basic', ['src/*.c'] )
```

---

# config #
A command object that can generate a config.h-type file based on internal variables.
## Options ##
  * `config`
    * A dictionary creating associations between keys and values.  If objects are given as a value, their config\_header() method will be called if it exists.  Otherwise, they will be converted to either 1 or 0 depending on whether they evaluate as true or false, respectively.
  * `output='./config.h'`
    * Where to place the output header.
## Examples ##
```
compiler = env.load( 'ccompiler' )

math = compiler.lib( 'math', headers=['math.h'], libs=['m'] )
foo = compiler.lib( 'foo', headers=['_foo.h'], required=False )
	
config = {'MATH_H': math,
    'FOO_H': foo }
config_header = env.load( 'config', config=config )
```
This will produce a file like this:
```
#ifndef __CONFIG_H__
#define __CONFIG_H__

#define MATH_H 1

#endif
```

---

# pkgconfig #
Compile and link against a [pkg-config](http://pkg-config.freedesktop.org/) package.  This may or may not work depending on your compiler; it will pass the --msvc-syntax option if Microsoft Visual C++ is being used.  Which it won't be given that msvc is not yet a supported compiler.  But it's the thought that counts.

Right now functionality is limited; specific package versions cannot be used.
### Options ###
  * compiler
    * The compiler to use.  Right now, this is only checked to see if msvc is being used; for that reason this particular API is volatile while I figure out a more graceful way to handle this.
  * pkg
    * The name of the package to link to.
  * required=True
    * Whether or not compilation should fail if this package isn't found.
### Example ###
```
compiler = env.load( 'ccompiler' )
glib = env.load( 'pkgconfig', compiler=compiler, pkg='glib-2.0' )
test = compiler.program( 'test', ['src/*.c'], libs=[ncurses,glib] )
```

---

# platform #
Detects platform-specific information, and allows checking for supported operating systems.  Each operating system has two parts, as shown.
  * posix
    * linux
    * freebsd
  * windows
On Linux, both linux and posix apply, for instance.
## Options ##
  * supported
    * Lists operating systems supported by this package.
  * unsupported
    * Lists operating systems not supported by this package.
## Attributes ##
  * copy
    * Path to the copy system utility.  On posix this will refer to cp, while on Windows it will refer to copy.
  * delete
    * Path to the delete system utility.  On posix this will refer to rm, while on Windows it will refer to del.
  * move
    * Path to the move system utility.  On posix this will refer to mv, while on Windows it will refer to move.
In addition, attributes will be set for the given platform.  For instance, the posix attribute will be set on Linux and `*`BSD.
## Example ##
```
# Reject Windows and Linux, but accept other Unix platforms.
os = self.env.load( 'platform', unsupported=['windows', 'linux'] )
```