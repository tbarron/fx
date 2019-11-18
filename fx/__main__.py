"""
Usage:
    fx [-d] [-n] [-q] cmd COMMAND FILE ...
    fx [-d] [-n] [-q] xargs COMMAND
    fx [-d] [-n] [-q] count COMMAND -i RANGE
    fx [-d] [-n] [-q] rename -e SUBSTITUTION FILE ...

Options:
    -d        debug -- run the python debugger
    -n        dryrun -- just show what would happen
    -q        quiet -- don't echo commands before running them
    -e        SUBSTITUTION -- a substitute expression: s/foo/bar/
    -i RANGE  <low number>:<high number>
"""


from docopt_dispatch import dispatch
from fx import xw_sub
import os
import pdb
import re
import sys
import tbx


# -----------------------------------------------------------------------------
@dispatch.on('cmd')
def fx_cmd(**kw):
    """
    Run the command for each filename in arglist.
    """
    if kw['d']:
        pdb.set_trace()
    cmd_t = kw['COMMAND']
    (dryrun, quiet) = (kw['n'], kw['q'])
    for filename in kw['FILE']:
        cmd = tbx.expand(re.sub('%', filename, cmd_t))
        dq_run(cmd, dryrun, quiet)


# -----------------------------------------------------------------------------
@dispatch.on('count')
def fx_count(**kw):
    """
    Run a command once for each of a sequence of numbers.

    Possible enhancements would be to handle low/high/step tuples, and
    to handle an arbitrary comma delimited list of values.
    """
    if kw['d']:
        pdb.set_trace()
    cmd_t = kw['COMMAND']
    (dryrun, quiet) = (kw['n'], kw['q'])
    (low, high) = kw['i'].split(':')
    for num in range(int(low), int(high)+1):
        cmd = tbx.expand(re.sub('%', str(num), cmd_t))
        dq_run(cmd, dryrun, quiet)


# -----------------------------------------------------------------------------
@dispatch.on('rename')
def fx_rename(**kw):
    """
    Create and run a rename command based on a s/old/new/ expression.
    """
    if kw['d']:
        pdb.set_trace()
    subst = kw['SUBSTITUTION']
    (dryrun, quiet) = (kw['n'], kw['q'])
    pieces = subst.split(subst[1])
    for filename in kw['FILE']:
        newname = re.sub(pieces[1], pieces[2], filename)
        if dryrun:
            print("would rename {} to {}".format(filename, newname))
        elif quiet:
            os.rename(filename, newname)
        else:
            print("renaming {} -> {}".format(filename, newname))
            os.rename(filename, newname)


# -----------------------------------------------------------------------------
@dispatch.on('xargs')
def fx_xargs(**kw):
    """
    Bundle arguments into command lines similarly to xargs.

    Unlike xargs, this version allows for static values following the
    list of arguments on each command line.
    """
    if kw['d']:
        pdb.set_trace()
    (dryrun, quiet) = (kw['n'], kw['q'])
    cmd_t = kw['COMMAND']
    for cmd in xargs_wrap(cmd_t):
        dq_run(cmd, dryrun, quiet)


# -----------------------------------------------------------------------------
def dq_run(cmd, dryrun, quiet):
    """
    Handle a command subject to the dryrun and quiet members of options.

    !dryrun & !quiet: display cmd then run
    !dryrun & quiet:  run without displaying first
    dryrun & !quiet:  display cmd without running it
    dryrun & quiet:   do nothing -- no display, no run
    """
    if dryrun:
        print("would do '{}'".format(cmd))
    elif quiet:
        result = tbx.run(cmd)
        print(result.rstrip())
    else:
        print(cmd)
        result = tbx.run(cmd)
        print(result.rstrip())


# ---------------------------------------------------------------------------
def xargs_wrap(cmd, rble=None):
    """
    Do xargs wrapping to cmd, distributing args from file rble across
    command lines.
    """
    def clean(nubbin):
        return re.sub(r'\s*%(\s*)', r'\1', nubbin)

    rble = rble or sys.stdin
    tcmd = cmd
    rval = []
    for line in rble:
        for item in line.strip().split(" "):
            tcmd = xw_sub(tcmd, item.strip())
            pending = True
            if 240 < len(tcmd):
                tcmd = clean(tcmd)
                rval.append(tcmd)
                pending = False
                tcmd = cmd
    if pending:
        tcmd = clean(tcmd)
        rval.append(tcmd)
    return(rval)


# -----------------------------------------------------------------------------
if __name__ == "__main__":
    dispatch(__doc__)
