import fx
import glob
import io
import re
import os
import tbx
import pytest


# -----------------------------------------------------------------------------
def test_flake():
    """
    Vet the code quality
    """
    result = tbx.run("flake8 fx test")
    assert result == ""


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd, item, exp", [
    ('/home/dir/one ~/%', 'two', '/home/dir/one /home/dir/two /home/dir/%'),
    ('~/%', 'one', '/home/dir/one /home/dir/%'),
    ('/home/dir/one /home/dir/two ~/%', 'three',
     '/home/dir/one /home/dir/two /home/dir/three /home/dir/%'),

    ('foobar', 'one', 'foobar one'),
    ('foobar one', 'two', 'foobar one two'),
    ('foobar %', 'one', 'foobar one %'),
    ('foobar%', 'one', 'foobarone foobar%'),
    ('foobarone foobar%', 'two', 'foobarone foobartwo foobar%'),

    ('foo%bar', 'one', 'fooonebar foo%bar'),
    ('fooonebar foo%bar', 'two', 'fooonebar footwobar foo%bar'),
    ('foo %bar', 'one', 'foo onebar %bar'),
    ('foo onebar %bar', 'two', 'foo onebar twobar %bar'),

    ('foo% bar', 'one', 'fooone foo% bar'),
    ('fooone foo% bar', 'two', 'fooone footwo foo% bar'),
    ('fooone footwo foo% bar', 'three', 'fooone footwo foothree foo% bar'),

    ('foo % bar', 'one', 'foo one % bar'),
    ('foo one % bar', 'two', 'foo one two % bar'),
    ('foo one two % bar', 'three', 'foo one two three % bar'),

    ('% foobar', 'one', 'one % foobar'),
    ('one % foobar', 'two', 'one two % foobar'),
    ('one two % foobar', 'three', 'one two three % foobar'),

    ('%foobar', 'one', 'onefoobar %foobar'),
    ('onefoobar %foobar', 'two', 'onefoobar twofoobar %foobar'),
    ('onefoobar twofoobar %foobar', 'three',
     'onefoobar twofoobar threefoobar %foobar'),

    ('~ %', 'one', '/home/dir one %'),
    ('/home/dir one %', 'two', '/home/dir one two %'),
    ('/home/dir one two %', 'three', '/home/dir one two three %'),

    ('% ~', 'one', 'one % /home/dir'),
    ('one % /home/dir', 'two', 'one two % /home/dir'),
    ('one two % /home/dir', 'three', 'one two three % /home/dir'),

    ('%~', 'one', 'one/home/dir %/home/dir'),
    ('one/home/dir %/home/dir', 'two', 'one/home/dir two/home/dir %/home/dir'),
    ('one/home/dir two/home/dir %/home/dir', 'three',
     'one/home/dir two/home/dir three/home/dir %/home/dir'),

    ('$USER%', 'one', 'userone user%'),
    ('userone user%', 'two', 'userone usertwo user%'),
    ('userone usertwo user%', 'three', 'userone usertwo userthree user%'),

    ('$USER %', 'one', 'user one %'),
    ('user one %', 'two', 'user one two %'),
    ('user one two %', 'three', 'user one two three %'),

    ('% $USER', 'one', 'one % user'),
    ('one % user', 'two', 'one two % user'),
    ('one two % user', 'three', 'one two three % user'),

    ('%$USER', 'one', 'oneuser %user'),
    ('oneuser %user', 'two', 'oneuser twouser %user'),
    ('oneuser twouser %user', 'three', 'oneuser twouser threeuser %user'),
    ])
def test_xw_sub(cmd, item, exp):
    """
    If a '%' appears in cmd, determine the word it appears in and then replace
    that word with the item followed by the % word. By calling xw_sub
    repeatedly, we can stuff item after item into the original command string.
    """
    pytest.dbgfunc()
    with tbx.envset(HOME='/home/dir', USER='user'):
        assert fx.xw_sub(cmd, item) == exp


# -----------------------------------------------------------------------------
def test_xw_nopct_file(fx_batch):
    """
    Tests for xargs_wrap(cmd: str, rble: fileobj)

      - cmd may contain '%', or not
      - fileobj may be an open file, sys.stdin, a StringIO

    What xargs_wrap is supposed to do, is, given a *cmd* like 'foo % bar', it
    takes lexical items from *rble* and constructs strings of the form

        'foo item1 item2 item3 ... itemn bar'

    such that the strings are only minimally longer than 240 bytes. This is
    like xargs except that I've never figured out a way to get xargs to embed
    stuff in the middle of the command -- it only wants to put stuff at the
    end.

    If *cmd* does not contain a % character (or if all the % chars are
    escaped), xargs_wrap should put the items at the end of cmd.
    """
    pytest.dbgfunc()
    tmppath, data = fx_batch
    with open(tmppath, 'r') as fobj:
        result = fx.xargs_wrap("echo", fobj)
    assert result == data


# -----------------------------------------------------------------------------
def test_xw_nopct_sio(fx_batch):
    """
    See docstring for test_xw_nopct_file above
    """
    pytest.dbgfunc()
    fobj = io.StringIO("".join(["{}\n".format(idx)
                                for idx in range(1, 250)]))
    tmppath, data = fx_batch
    result = fx.xargs_wrap("echo", fobj)
    assert result == data


# -----------------------------------------------------------------------------
def test_xw_pct_file(fx_batch):
    """
    See docstring for test_xw_nopct_file above
    """
    pytest.dbgfunc()
    tmppath, data = fx_batch
    data = exp_xargs_data("echo ", [83, 146, 205, 250])
    with open(tmppath, 'r') as fobj:
        result = fx.xargs_wrap("echo %", fobj)
    assert result == data


# -----------------------------------------------------------------------------
def test_xw_pct_sio(fx_batch):
    """
    See docstring for test_xw_nopct_file above
    """
    pytest.dbgfunc()
    fobj = io.StringIO("".join(["{}\n".format(idx)
                                for idx in range(1, 250)]))
    tmppath, data = fx_batch
    data = exp_xargs_data("echo ", [83, 146, 205, 250])
    result = fx.xargs_wrap("echo %", fobj)
    assert result == data


# -----------------------------------------------------------------------------
def test_xargs_cmdl_stdin(tmpdir):
    """
    Run 'ls /usr/include/nfs | fx -n -x -c "echo foo % bar"'

    Expected output: 'foo <file> <file> <file> ... <file> bar'
    """
    pytest.dbgfunc()
    ilst = "one two three four".split()

    exp = "would do 'echo foo {} bar'\n".format(" ".join(ilst))
    result = tbx.run("python fx xargs -n \"echo foo % bar\"",
                     input="\n".join(ilst))
    assert result == exp


# -----------------------------------------------------------------------------
def test_batch_command_both(tmpdir, capsys, fx_batch):
    """
    Test batch_command with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    v = {'-n': True, '-q': True, '-x': True, 'COMMAND': "echo %"}
    tmppath, data = fx_batch
    data = exp_xargs_data("would do 'echo ", [83, 146, 205, 250])
    exp = "".join("{}'\n".format(line) for line in data)
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
    data = exp_xargs_data("would do 'echo ", [83, 146, 205, 250])
    exp = "".join("{}'\n".format(line) for line in data)
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
    data = exp_xargs_data("", [83, 146, 205, 250])
    exp = ''
    for line in data:
        exp += "echo {}\n".format(line)
        exp += "{}\n".format(line)

    with open(tmppath, 'r') as f:
        fx.batch_command(v, [], f)
    assert exp.split("\n") == "".join(capsys.readouterr()).split("\n")


# -----------------------------------------------------------------------------
def test_batch_command_quiet(tmpdir, capsys, fx_batch):
    """
    Test batch_command with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    v = {'-n': False, '-q': True, '-x': True, 'COMMAND': "echo %"}
    tmppath, data = fx_batch
    data = exp_xargs_data("", [83, 146, 205, 250])
    exp = ''
    for line in data:
        exp += "{}\n".format(line)

    with open(tmppath, 'r') as f:
        fx.batch_command(v, [], f)
    assert exp.split("\n") == "".join(capsys.readouterr()).split("\n")


# -----------------------------------------------------------------------------
def test_fx_short_help():
    """
    Verify that 'fx --help' does the right thing
    """
    pytest.dbgfunc()
    exp_l = ["Usage:",
             "    fx [-d] [-n] [-q] cmd COMMAND FILE ...",
             "    fx [-d] [-n] [-q] xargs COMMAND",
             "    fx [-d] [-n] [-q] count COMMAND -i RANGE",
             "    fx [-d] [-n] [-q] rename -e SUBSTITUTION FILE ...",
             "    fx [-d] version",
             ]
    result = tbx.run("python fx help")
    assert result == "\n".join(exp_l) + "\n"


# -----------------------------------------------------------------------------
def test_fx_long_help():
    """
    Verify that 'fx --help' does the right thing
    """
    pytest.dbgfunc()
    exp_l = ["Usage:",
             "    fx [-d] [-n] [-q] cmd COMMAND FILE ...",
             "    fx [-d] [-n] [-q] xargs COMMAND",
             "    fx [-d] [-n] [-q] count COMMAND -i RANGE",
             "    fx [-d] [-n] [-q] rename -e SUBSTITUTION FILE ...",
             "    fx [-d] version",
             "",
             "Options:",
             "    -d        debug -- run the python debugger",
             "    -n        dryrun -- just show what would happen",
             "    -q        quiet -- don't echo commands before running them",
             "    -e        SUBSTITUTION -- a substitute expression: "
             "s/foo/bar/",
             "    -i RANGE  <low number>:<high number>",
             ]
    result = tbx.run("python fx --help")
    assert result == "\n".join(exp_l) + "\n"


# -----------------------------------------------------------------------------
def test_iterate_command_both(tmpdir, capsys):
    """
    Test iterate_command() with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': True, '-q': True, 'COMMAND': "echo %",
             '-i': True, 'RANGE': "5:10"}
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_dryrun(tmpdir, capsys):
    """
    Test iterate_command() with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': True, '-q': False, 'COMMAND': "echo %",
             '-i': True, 'RANGE': "5:10"}
        exp = "".join(["would do 'echo %d'\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_neither(tmpdir, capsys):
    """
    Test iterate_command() with dryrun False and quiet False.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': False, '-q': False, 'COMMAND': "echo %",
             '-i': True, 'RANGE': "5:10"}
        exp = "".join(["echo %d\n%d\n" % (i, i) for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_iterate_command_quiet(tmpdir, capsys):
    """
    Test iterate_command() with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': False, '-q': True, 'COMMAND': "echo %",
             '-i': True, 'RANGE': "5:10"}
        exp = "".join(["%d\n" % i for i in range(5, 10)])

        fx.iterate_command(v, [])
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_both(capsys):
    """
    Test routine psys with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    v = {'-n': True, '-q': True}
    expected = "would do 'ls -d fx.py'\n"
    fx.psys('ls -d fx.py', v)
    assert expected in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_dryrun(capsys):
    """
    Test routine psys with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    v = {'-n': True, '-q': False}
    expected = "would do 'ls -d nosuchfile'\n"
    fx.psys('ls -d nosuchfile', v)
    assert expected in "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_neither(capsys):
    """
    Test routine psys with dryrun False and quiet False.
    """
    pytest.dbgfunc()
    root = tbx.dirname(os.path.abspath(__file__), level=2)
    v = {'-n': False, '-q': False}
    expected = "ls -d %s/fx\n%s/fx\n" % (root, root)
    fx.psys('ls -d %s/fx' % root, v)
    assert expected in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_psys_quiet(tmpdir, capsys, data):
    """
    Test routine psys with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        exp = "a.xyzzy\nb.xyzzy\nc.xyzzy\ntmpfile\n"
        v = {'-n': False, '-q': True}
        fx.psys('ls', v)
        assert exp == "".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_both(tmpdir, capsys):
    """
    Test subst_command() with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': True, '-q': True, 'COMMAND': "ls %"}
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        fx.subst_command(v, a)
        assert exp in "".join(capsys.readouterr())


# -----------------------------------------------------------------------
def test_subst_command_dryrun(tmpdir, capsys):
    """
    Test subst_command() with dryrun True and quiet False.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': True, '-q': False, 'COMMAND': "ls %"}
        a = ['a.pl', 'b.pl', 'c.pl']
        exp = "".join(["would do 'ls %s'\n" % x for x in a])
        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_neither(tmpdir, capsys):
    """
    Test subst_command() with dryrun False and quiet False.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': False, '-q': False, 'COMMAND': "ls %"}
        a = ['a.pl', 'b.pl', 'c.pl']
        for x in a:
            tmpdir.join(x).ensure()
        exp = "".join(['ls %s\n%s\n' % (x, x) for x in a])
        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_command_quiet(tmpdir, capsys):
    """
    Test subst_command() with dryrun False and quiet True.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        v = {'-n': False, '-q': True, 'COMMAND': "ls %"}
        a = ['a.pl', 'b.pl', 'c.pl']
        for x in a:
            tmpdir.join(x).ensure()
        exp = "".join(['%s\n' % x for x in a])
        fx.subst_command(v, a)
        assert exp in " ".join(capsys.readouterr())


# -----------------------------------------------------------------------------
def test_subst_rename_both(tmpdir, capsys):
    """
    Test subst_rename() with dryrun True and quiet True.
    """
    pytest.dbgfunc()
    with tbx.chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            tmpdir.join(a).ensure()
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = {'-n': True, '-q': True, '-e': True,
             'SUBSTITUTION': "s/.pl/.xyzzy"}
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
    with tbx.chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            tmpdir.join(a).ensure()
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        v = {'-n': True, '-q': False, '-e': True,
             'SUBSTITUTION': "s/.pl/.xyzzy"}
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
    with tbx.chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            tmpdir.join(a).ensure()
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = {'-n': False, '-q': False, '-e': True,
             'SUBSTITUTION': "s/.pl/.xyzzy"}
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
    with tbx.chdir(tmpdir.strpath):
        arglist = ['a.pl', 'b.pl', 'c.pl']
        for a in arglist:
            tmpdir.join(a).ensure()
        expected = "".join(['rename %s.pl %s.xyzzy\n' % (x, x) for x in
                            [q.replace('.pl', '') for q in arglist]])
        exp = [re.sub('.pl', '.xyzzy', x) for x in arglist]
        v = {'-n': False, '-q': True, '-e': True,
             'SUBSTITUTION': "s/.pl/.xyzzy"}
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
def test_version():
    """
    Running 'fx version' should report the current fx version
    """
    pytest.dbgfunc()
    result = tbx.run("python fx version")
    assert result == "fx {}\n".format(fx.version.__version__)


# ---------------------------------------------------------------------------
def exp_xargs_data(prefix, knees):
    """
    Construct a set of expected data for xargs_wrap and batch_command
    """
    rval = []
    lo = 1
    for hi in knees:
        rval.append(prefix + " ".join([str(idx) for idx in range(lo, hi)]))
        lo = hi
    return rval


# ---------------------------------------------------------------------------
@pytest.fixture
def fx_batch(tmpdir):
    """
    Set up data for the batch command tests
    """
    tmpfile = tmpdir.join('tmpfile')
    data = [str(x) + '\n' for x in range(1, 250)]
    tmpfile.write("".join(data))
    rval = exp_xargs_data("echo ", [83, 147, 207, 250])
    return tmpfile.strpath, rval


# ---------------------------------------------------------------------------
@pytest.fixture
def data(tmpdir, request):
    """
    set up some data
    """
    if request.function.__name__ == "test_psys_quiet":
        for stem in ['a.xyzzy', 'b.xyzzy', 'c.xyzzy', 'tmpfile']:
            path = tmpdir.join(stem)
            path.ensure()
