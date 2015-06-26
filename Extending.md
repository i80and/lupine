# Intro & Example #
The lupine source directory has a `commands` directory in it that contains files such as `command_ccompiler.py` or `command_config.py`.  These are command objects.  The naming scheme is not just a formality; it's how the parser knows what to load.  All command objects are named `command_[name].py`.

Here is an example command object that displays the basics of extending lupine without actually doing anything useful.  Specifically, it will take a message option and print it.  We save it into `commands/command_foobar.py`
```
class foobar:
        # Initialization is strictly optional, but can be used to set properties and other such tasks as soon as it is created.  It will not, however, be able to access its options.
        def __init__( self, env, result='' ):
                self.env.output.start( 'Outputting message' )
                self.result = result

                if result:
                        self.env.output.success( self['message'] )
                else:
                        self.env.output.error( 'No message specified' )
                
        def __nonzero__( self ):
                'Evaluate this object as true or false'
                return self.result
```

# APIs #
## Environment ##
The environment provides access to the wider world, so to speak.  Through it, a command object may find a program on the system, write to the Makefile, etc.  It is referenced in all command objects through the env variable.
  * `load( self, name, **args )`
  * `find_program( self, name )`
  * `escape_whitespace( self, str )`
  * `escape( self, str, char )`

  * `output.start( self, task )`
  * `output.success( self, message )`
  * `output.warning( self, message )`
  * `output.error( self, message )`
  * `output.comment( self, message, error=False )`

  * `make.add_rule( self, target, deps, commands, phony=False, default=False )`
  * `make.add_macro( self, name, command )`
  * `make.add_clean( self, command )`