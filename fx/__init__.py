"""
command effects

The simplest use is to apply a command to a sequence of files. For example,

    fx -c 'echo %' file1 file2 file3

will expand to

    echo file1
    echo file2
    echo file3

Usage:
    fx [-d] [-n] [-q] -c COMMAND FILE ...
    fx [-d] [-n] [-q] -x -c COMMAND
    fx [-d] [-n] [-q] -i RANGE -c COMMAND
    fx [-d] [-n] [-q] -e SUBSTITUTION FILE ...

Options
    -d        debug -- run the python debugger
    -n        dryrun -- just show what would happen
    -q        quite -- don't echo commands before running them
    -c        COMMAND ('%' is replaced with each FILE in turn)
    -e        SUBSTITUTION -- a substitute expression: s/foo/bar/
    -i        RANGE -- <low number>:<high number>
    -x        Bundle strings from stdin like xargs into '%'


LICENSE

Copyright (C) 1995 - <the end of time>  Tom Barron
  tom.barron@comcast.net
  177 Crossroads Blvd
  Oak Ridge, TN  37830

This software is licensed under the CC-GNU GPL. For the full text of
the license, see http://creativecommons.org/licenses/GPL/2.0/

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
import docopt
import os
import pdb
import re
import sys
import tbx


# -----------------------------------------------------------------------------
def main():
    """
    main entrypoint
    """
    opts = docopt.docopt(__doc__)
    if opts['-d']:
        pdb.set_trace()
    print(opts)

    if opts['-e']:
        subst_rename(opts)
    elif opts['-i']:
        iterate_command(opts)
    elif opts['-x']:
        batch_command(opts)
    elif opts['-c']:
        subst_command(opts)


# ---------------------------------------------------------------------------
def batch_command(options, arglist, rble=sys.stdin):
    """
    Bundle arguments into command lines similarly to xargs.

    Unlike xargs, this version allows for static values following the
    list of arguments on each command line.
    """
    for cmd in xargs_wrap(options['COMMAND'], rble):
        psys(cmd, options)


# ---------------------------------------------------------------------------
def iterate_command(options, arglist):
    """
    Run a command once for each of a sequence of numbers.

    Possible enhancements would be to handle low/high/step tuples, and
    to handle an arbitrary comma delimited list of values.
    """
    (low, high) = options['-i'].split(':')
    for idx in range(int(low), int(high)):
        cmd = tbx.expand(re.sub('%', str(idx), options['COMMAND']))
        psys(cmd, options)


# ---------------------------------------------------------------------------
def psys(cmd, options):
    """
    Handle a command subject to the dryrun and quiet members of options.

    !dryrun & !quiet: Display the command, then run it
    !dryrun & quiet: Run the command without displaying it
    dryrun & !quiet: Display the command without running it
    dryrun & quiet: Do nothing - no display, no run
    """
    # print("psys: cmd = '%s', dryrun = %s, quiet = %s"
    #       % (cmd, options.dryrun, options.quiet))
    if options['-n']:
        print("would do '%s'" % cmd)
    elif options['-q']:
        # os.system(cmd)
        pipe = os.popen(cmd, 'r')
        sys.stdout.write(pipe.read())
        pipe.close()
    else:
        print(cmd)
        # os.system(cmd)
        pipe = os.popen(cmd, 'r')
        sys.stdout.write(pipe.read())
        pipe.close()


# ---------------------------------------------------------------------------
def subst_command(options, arglist):
    """
    Run the command for each filename in arglist.
    """
    for filename in arglist:
        cmd = tbx.expand(re.sub('%', filename, options['COMMAND']))
        psys(cmd, options)


# ---------------------------------------------------------------------------
def subst_rename(options, arglist):
    """
    Create and run a rename command based on a s/old/new/ expression.
    """
    subst = options['SUBSTITUTION']
    pieces = subst.split(subst[1])
    for filename in arglist:
        newname = re.sub(pieces[1], pieces[2], filename)
        print("rename %s %s" % (filename, newname))
        if not options['-n']:
            os.rename(filename, newname)


# ---------------------------------------------------------------------------
def usage():
    """
    Report program usage.
    """
    return """
    fx [-n] -c <command> <files> (% in the command becomes filename)
            -e s/old/new/ <files> (rename file old to new name)
            -i low:high -c <command> (% ranges from low to high-1)
            """


# ---------------------------------------------------------------------------
def xargs_wrap(cmd, rble):
    """
    Do xargs wrapping to cmd, distributing args from file rble across
    command lines.
    """
    tcmd = cmd
    rval = []
    for line in rble:
        bline = line.strip()
        for item in bline.split(" "):
            tcmd = tbx.expand(re.sub('%', item + ' %', tcmd))
            pending = True

            if 240 < len(tcmd):
                tcmd = re.sub(r'\s*%\s*', '', tcmd)
                rval.append(tcmd)
                pending = False
                tcmd = cmd
    if pending:
        tcmd = re.sub(r'\s*%\s*', '', tcmd)
        rval.append(tcmd)
    return(rval)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    main()
