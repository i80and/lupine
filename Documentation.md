# Intro #
Lupine project descriptions are written in the form of a Python script called `project.lupine` in your project's root.  It has two global functions: `configure( env )` used to add configuration options, and `build( env, args )` used to create Make rules.

# Loading Command Objects #
Most of the functionality in Lupine is implemented by loading command objects.  Often a variable name such as `env` will be given, that represents an Environment object.  It has a load method taking as its first argument the name of the object to load (index of available options in the sidebar), followed by a set of arguments to pass to it.

# Sample #
```
def configure( env ):
    pass

def build( env, args ):
    compiler = env.load( 'ccompiler' )
    test = compiler.program( 'test', ['src/*.c'] )
```

# Further Learning #
  * CommandObjectReference
  * [Extending](Extending.md)