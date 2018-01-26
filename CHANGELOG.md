## 0.0.8 ... 

 * Clean up tests and code for replstr
 * Ensure range and cmd have replstr support
 * Make messages consistent among cmd, range, and xargs

## 0.0.7 ... 2018.0125 16:16:43

 * Move the help display toward consistency with regard to capitalization
 * Add tests for rename subcommand
 * Implement rename subcommand
 * Add tests for xargs subcommand
 * Implement xargs subcommand

## 0.0.6 ... 2018.0124 13:03:49

 * Generalized file reading with the function read_file(). Both perrno()
   and _get_cargo_version() use this.
 * Base perrno on /usr/include/sys/errno.h rather than the errno values
   python knows about. This involved dragging in the regex package and its
   dependencies.
 * Add README.md

## 0.0.5 ... 2018.0122 17:47:30

 * Add --binary support to 'fx mag'
 * Use unit-free prefixes by default, "b" for units with --binary
 * Remove run() from range.rs
 * Replace rename() and xargs() stubs in main.rs with modules
 * Add tests and code for perrno

## 0.0.4 ... 2018.0120 13:08:21

 * Update 'fx range help' output to be consistent
 * Make subcommands versionless
 * Starting CHANGELOG
