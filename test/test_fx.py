# import pdb
# pdb.set_trace()
import fx
# from bscr import util as U
import glob
import re
import optparse
import pexpect
import tbx
import pytest


# -----------------------------------------------------------------------------
def test_batch_command_both(tmpdir, capsys, fx_batch):
    """
    Test batch_command with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    v = {'-n': True, '-q': True, '-x': True, 'COMMAND': "echo %"}
    tmppath, data = fx_batch
    exp = ''
    for chunk in data:
        exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"
    with open(tmppath, "r") as f:
        fx.batch_command(v, [], f)
    assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_batch_command_dryrun(tmpdir, capsys, fx_batch):
    """
    Test batch_command with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    v = {'-n': True, '-q': False, '-x': True, 'COMMAND': "echo %"}
    tmppath, data = fx_batch
    exp = ''
    for chunk in data:
        exp += re.sub('^echo ', "would do 'echo ", chunk) + "'\n"
    with open(tmppath, 'r') as f:
        fx.batch_command(v, [], f)
    assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_batch_command_neither(tmpdir, capsys, fx_batch):
    """
    Test batch_command with dryrun and quiet both False.
    """
    pytest.dbgfunc()
    v = {'-n': False, '-q': False, '-x': True, 'COMMAND': "echo %"}
    tmppath, data = fx_batch
    exp = ''
    for chunk in data:
        exp += chunk + '\n'
        exp += re.sub('^echo ', '', chunk) + '\n'
    with open(tmppath, 'r') as f:
        fx.batch_command(v, [], f)
    assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_batch_command_quiet(tmpdir, capsys, fx_batch):
    """
    Test batch_command with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    v = {'-n': False, '-q': True, '-x': True, 'COMMAND': "echo %"}
    tmppath, data = fx_batch
    exp = ''
    for chunk in data:
        exp += re.sub('^echo ', '', chunk) + '\n'

    with open(tmppath, 'r') as f:
        fx.batch_command(v, [], f)
    assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_fx_help():
    """
    Verify that 'fx --help' does the right thing
    """
    pytest.dbgfunc()
    exp_l = ["Usage:",
             "fx [-d] [-n] [-q] -c COMMAND FILE ...",
             "fx [-d] [-n] [-q] -x -c COMMAND",
             "fx [-d] [-n] [-q] -i RANGE -c COMMAND",
             "fx [-d] [-n] [-q] -e SUBSTITUTION FILE ...",
             "Options",
             "-d        debug -- run the python debugger",
             "-n        dryrun -- just show what would happen",
             "-q        quiet -- don't echo commands before running them",
             "-c       COMMAND (% is replaced with each FILE in turn)",
             "-e       SUBSTITUTION -- a substitute expression: s/foo/bar/",
             "-i       RANGE -- <low number>:<high number>",
             "-x       Bundle strings from stdin like xargs into '%'",
             "",
             "-i low:high -c <command> (% ranges from low to high-1)",
             "Options:",
             "",
             "-c CMD, --command=CMD",
             "command to apply to all arguments",
             "-d, --debug           run under the debugger",
             "-e EDIT, --edit=EDIT  file rename expression applied to " +
             "all arguments",
             " -i IRANGE, --integer=IRANGE",
             "low:high -- generate range of numbers",
             "-n, --dry-run         dryrun or execute",
             "-q, --quiet           don't echo commands, just run them",
             "-x, --xargs           batch input from stdin into command" +
             " lines like xargs",
             ]
    # script = U.script_location("fx")
    script = pexpect.which('fx')
    result = pexpect.run("%s --help" % script).decode()
    for exp_s in exp_l:
        assert exp_s in result


# -----------------------------------------------------------------------------
def test_iterate_command_both(tmpdir, capsys):
    """
    Test iterate_command() with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': True,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_dryrun(tmpdir, capsys):
    """
    Test iterate_command() with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_neither(tmpdir, capsys):
    """
    Test iterate_command() with dryrun False and quiet False.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["echo %d\n%d\n" % (i, i) for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_quiet(tmpdir, capsys):
    """
    Test iterate_command() with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'cmd': 'echo %',
                             'irange': '5:10'})
        exp = "".join(["%d\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_both(capsys):
    """
    Test routine psys with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    v = optparse.Values({'dryrun': True, 'quiet': True})
    expected = "would do 'ls -d fx.py'\n"
    fx.psys('ls -d fx.py', v)
    assert expected in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_dryrun(capsys):
    """
    Test routine psys with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    v = optparse.Values({'dryrun': True, 'quiet': False})
    expected = "would do 'ls -d nosuchfile'\n"
    fx.psys('ls -d nosuchfile', v)
    assert expected in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_neither(capsys):
    """
    Test routine psys with dryrun False and quiet False.
    """
    pytest.dbgfunc()
    root = U.findroot()
    v = optparse.Values({'dryrun': False, 'quiet': False})
    expected = "ls -d %s/fx.py\n%s/fx.py\n" % (root, root)
    fx.psys('ls -d %s/fx.py' % root, v)
    assert expected in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_quiet(tmpdir, capsys, data):
    """
    Test routine psys with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        exp = "a.xyzzy\nb.xyzzy\nc.xyzzy\ntmpfile\n"
        v = optparse.Values({'dryrun': False, 'quiet': True})
        fx.psys('ls', v)
        assert exp == "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_both(tmpdir, capsys):
    """
    Test subst_command() with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': True, 'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        U.safe_unlink(a)

        fx.subst_command(v, a)
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------
def test_subst_command_dryrun(tmpdir, capsys):
    """
    Test subst_command() with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        U.safe_unlink(a)

        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_neither(tmpdir, capsys):
    """
    Test subst_command() with dryrun False and quiet False.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
        U.touch(a)

        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_quiet(tmpdir, capsys):
    """
    Test subst_command() with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'cmd': 'ls %'})
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(['%s\n' % x for x in a])
        U.touch(a)

        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_rename_both(tmpdir, capsys):
    """
    Test subst_rename() with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = optparse.Values({'dryrun': True, 'quiet': True,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

        q = glob.glob('*.pl')
        q.sort()
        assert q == arglist


# -----------------------------------------------------------------------------
def test_subst_rename_dryrun(tmpdir, capsys):
    """
    Test subst_rename() with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = optparse.Values({'dryrun': True, 'quiet': False,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

        q = glob.glob('*.pl')
        q.sort()
        assert q == arglist


# -----------------------------------------------------------------------------
def test_subst_rename_neither(tmpdir, capsys):
    """
    Test subst_rename() with dryrun False and quiet False.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = optparse.Values({'dryrun': False, 'quiet': False,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

        q = glob.glob('*.xyzzy')
        q.sort()
        assert exp == q


# -----------------------------------------------------------------------------
def test_subst_rename_quiet(tmpdir, capsys):
    """
    Test subst_rename() with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    with U.Chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            U.touch(a)
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = optparse.Values({'dryrun': False, 'quiet': True,
                             'edit': 's/.pl/.xyzzy'})

        fx.subst_rename(v, arglist)
        assert expected in " ".join(capsys.readouterr())

        q = glob.glob('*.pl')
        q.sort()
        assert [] == q

        q = glob.glob('*.xyzzy')
        q.sort()
        assert exp == q


# -----------------------------------------------------------------------------
def test_usage():
    """
    Test the Usage routine.
    """
    pytest.dbgfunc()
    exp = '\n'
    exp += '    fx [-n] -c <command> <files> (% in the command becomes'
    exp += ' filename)\n'
    exp += '            -e s/old/new/ <files> (rename file old to new'
    exp += ' name)\n'
    exp += '            -i low:high -c <command> (% ranges from low to'
    exp += ' high-1)\n            '
    actual = fx.usage()
    assert exp == actual


# ---------------------------------------------------------------------------
@pytest.fixture
def fx_batch(tmpdir):
    """
    Set up data for the batch command tests
    """
    tmpfile = tmpdir.join('tmpfile')
    data = [str(x) + '\n' for x in range(1, 250)]
    tmpfile.write("".join(data))
    with open(tmpfile.strpath, 'r') as f:
        rval = fx.xargs_wrap("echo %", f)
    return tmpfile.strpath, rval
    
# ---------------------------------------------------------------------------
@pytest.fixture
def data(tmpdir, request):
    """
    set up some data
    """
    if request.function.func_name == "test_psys_quiet":
        for stem in ['a.xyzzy', 'b.xyzzy', 'c.xyzzy', 'tmpfile']:
            path = tmpdir.join(stem)
            path.ensure()
