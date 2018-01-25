import contextlib
import glob
import itertools
import os
import pdb
import pexpect
import py
import pytest
import tbx


# -----------------------------------------------------------------------------
def test_cargo_build():
    """
    Check whether the target is out of date and if so run 'cargo build'
    """
    build = False
    target = "target/debug/fx"
    srcl = ["ascii", "cmd", "mag", "main", "odx", "perrno", "range", "rename", "xargs"]
    if any([not os.path.exists(target)] +
           [younger_than("src/{}.rs".format(x), target) for x in srcl]):
        result = runcmd("cargo build");
        assert "panic" not in result
        assert "error" not in result


# -----------------------------------------------------------------------------
def test_cargo_test():
    """
    Run 'cargo test' and verify its output reflects all tests passing
    """
    result = runcmd("cargo test")
    assert "panic" not in result
    assert "error" not in result


# -----------------------------------------------------------------------------
def test_help_contents():
    """
    Verify the contents of 'fx help'
    """
    result = runcmd("fx help")
    exp = ["fx [SUBCOMMAND]",
           "-h, --help       Prints help information",
           "-V, --version    Prints version information",
           "ascii     Show the ascii code table",
           "cmd       Replace % with arguments",
           "help      Prints this message or the help of the given "
           "subcommand(s)",
           "mag       Report the size of a number",
           "odx       Report hex, decimal, octal, and binary values",
           "perrno    Report errno values and meanings",
           "range     Replace % in command with numbers from <interval>",
           "rename    Rename files based on a s/foo/bar/ expr",
           "xargs     Replace % in command with clumps of args",
           ]
    for item in exp:
        assert item in result


# -----------------------------------------------------------------------------
def test_versionless_subcommands():
    """
    Verify that subcommands do not offer -V/--version option
    """
    cmd = "fx help cmd"
    result = runcmd(cmd)
    assert "-V, --version" not in result


# -----------------------------------------------------------------------------
def test_cmd_command_required():
    """
    Verify that 'fx cmd' requires a command string
    """
    cmd = "fx cmd"
    result = runcmd(cmd)
    exp = ["error:",
           "The following required arguments were not provided",
           "<command>",
           "<items>",
           "fx cmd [FLAGS] <command> <items>...",
           ]
    for item in exp:
        assert item in result


# -----------------------------------------------------------------------------
def test_cmd_items_required():
    """
    Verify that 'fx cmd <command>' complains about missing items
    """
    cmd = "fx cmd \"echo foo % bar\""
    result = runcmd(cmd)
    exp = ["error:",
           "The following required arguments were not provided",
           "<items>",
           "fx cmd [FLAGS] <command> <items>...",
           ]
    for item in exp:
        assert item in result


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd", [
    "fx cmd \"echo foo % bar\" one two three --dryrun",
    "fx cmd --dryrun \"echo foo % bar\" one two three",
    "fx cmd \"echo foo % bar\" one two three -n",
    "fx cmd -n \"echo foo % bar\" one two three",
    ])
def test_cmd_dryrun_supported(cmd):
    """
    Verify that 'fx cmd' supports the dryrun option in various positions
    """
    result = runcmd(cmd)
    exp = "".join(["would do 'echo foo {} bar'\r\n".format(x)
                   for x in ["one", "two", "three"]])
    assert result == exp


# -----------------------------------------------------------------------------
def test_cmd_optionals():
    """
    Verify that 'fx cmd' makes dryrun and verbose optional
    """
    result = runcmd("fx cmd \"echo foo % bar\" one two three")
    exp = "".join(["foo {} bar\r\n".format(x)
                   for x in ["one", "two", "three"]])
    assert result == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd", [
    "fx cmd \"echo foo % bar\" one two three -v",
    "fx cmd \"echo foo % bar\" one two three --verbose",
    "fx cmd -v \"echo foo % bar\" one two three",
    "fx cmd --verbose \"echo foo % bar\" one two three",
    ])
def test_cmd_verbose_supported(cmd):
    """
    Verify that 'fx cmd' supports the verbose option in various positions
    """
    result = runcmd(cmd)
    arglist = ["one", "two", "three"]
    body = "> echo foo {0} bar\r\nfoo {0} bar\r\n"
    exp = "".join([body.format(x) for x in arglist])
    assert result == exp


# -----------------------------------------------------------------------------
def test_mag_binary_opt():
    """
    Verify that -b/--binary shows up in 'fx help mag' output
    """
    cmd = "fx help mag"
    result = runcmd(cmd)
    assert "-b, --binary    Use divisor 1024" in result


# -----------------------------------------------------------------------------
def test_mag_no_binary():
    """
    Verify that 'fx mag' works without --binary
    """
    result = runcmd("fx mag 987654")
    assert "987.654 K" in result
    assert "b" not in result


# -----------------------------------------------------------------------------
def test_mag_binary():
    """
    Verify that 'fx mag' with --binary uses a 1024 divisor
    """
    result = runcmd("fx mag -b 2141232341")
    assert "1.994 Gb" in result


# -----------------------------------------------------------------------------
def test_perrno_noarg():
    """
    Try several perrno values to make sure 'fx perrno' returns the right thing
    """
    result = runcmd("fx perrno")
    exp = ["error:",
           "The following required arguments were not provided",
           "<name_or_number>",
           "fx perrno <name_or_number>",
           ]
    for item in exp:
        assert item in result


# -----------------------------------------------------------------------------
def test_perrno_nums():
    """
    Verify that 'fx perrno <number>' returns what is expected
    """
    result = runcmd("fx perrno 10 25 106 200")
    exp = "".join(["ECHILD (10): No child processes\r\n",
                   "ENOTTY (25): Inappropriate ioctl for device\r\n",
                   "EQFULL (106): Interface output queue is full\r\n"
                   "No error entry found for 200\r\n"
                   ])
    assert result == exp


# -----------------------------------------------------------------------------
def test_perrno_names():
    """
    Verify that 'fx perrno <name>' returns what is expected
    """
    result = runcmd("fx perrno EMLINK ENOLCK ENOSUCH")
    exp = "".join(["EMLINK (31): Too many links\r\n",
                   "ENOLCK (77): No locks available\r\n",
                   "No error entry found for ENOSUCH\r\n"
                   ])
    assert result == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd, xbody", [
    ("fx range \"echo foo % bar\" -i 10..15 -v",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ("fx range -v \"echo foo % bar\" -i 10..15",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ("fx range \"echo foo % bar\" -i 10..15 --verbose",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ("fx range --verbose \"echo foo % bar\" -i 10..15",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ])
def test_range_verbose_supported(cmd, xbody):
    """
    Verify that -v/--verbose is supported on 'fx range' in various positions
    """
    result = runcmd(cmd)
    exp = "".join([xbody.format(x) for x in range(10, 15)])
    assert result == exp


# -----------------------------------------------------------------------------
def test_range_command_required():
    """
    Verify that 'fx range' complains about the absence of any command string
    """
    cmd = "fx range"
    result = runcmd(cmd)
    exp = ["error:",
           "The following required arguments were not provided",
           "<command>",
           "--interval <interval>",
           "fx range [FLAGS] [OPTIONS] <command> --interval <interval>"
           ]
    for item in exp:
        assert item in result


# -----------------------------------------------------------------------------
def test_range_interval_required():
    """
    Verify that 'fx range <cmd>' complains about the absence of -i/--interval
    """
    cmd = "fx range \"echo foo %\""
    result = runcmd(cmd)
    exp = ["error:",
           "The following required arguments were not provided",
           "--interval <interval>",
           "fx range [FLAGS] [OPTIONS] <command> --interval <interval>"
           ]
    for item in exp:
        assert item in result


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd, xbody", [
    ("fx range \"echo foo % bar\" -i 10..15 -z 3", "foo {:03d} bar\r\n"),
    ("fx range -z 4 \"echo foo % bar\" -i 10..15", "foo {:04d} bar\r\n"),
    ("fx range \"echo foo % bar\" -i 10..15 --zpad 5", "foo {:05d} bar\r\n"),
    ("fx range --zpad 6 \"echo foo % bar\" -i 10..15", "foo {:06d} bar\r\n"),
    ])
def test_range_zpad_supported(cmd, xbody):
    """
    Verify that option -z/--zpad is supported in various positions
    """
    result = runcmd(cmd)
    exp = "".join([xbody.format(x) for x in range(10, 15)])
    assert result == exp


# -----------------------------------------------------------------------------
def test_range_optionals():
    """
    Run 'fx range' without the -z / --zpad option to verify it's not required.
    Also verifies that verbose and dryrun are optional
    """
    cmd = "fx range \"echo foo % bar\" -i 10..15"
    result = runcmd(cmd)
    exp = "".join(["foo {} bar\r\n".format(x) for x in range(10, 15)])
    assert result == exp


# -----------------------------------------------------------------------------
def test_rename_help():
    """
    Verify that the right stuff is in the output of 'fx help rename'
    """
    cmd = "fx help rename"
    result = runcmd(cmd)
    assert "Rename files based on a s/foo/bar/ expr" in result
    assert "(needs work)" not in result
    assert "-n, --dryrun     Report what would happen without acting" in result
    assert "-h, --help       Prints help information" in result
    assert "-v, --verbose    Report renames as they happen" in result
    assert "<substitute>    Edit expression: s/old/new/" in result
    assert "<items>...      Files to rename" in result


# -----------------------------------------------------------------------------
def test_rename_dryrun(tmpdir, fx_rename):
    """
    Verify that 'fx rename -n' behaves as expected
    """
    with chdir(tmpdir.strpath):
        cmd = "fx rename -n s/RENAME/NEW/ {}".format(" ".join(fx_rename))
        result = runcmd(cmd)
        for fname in fx_rename:
            assert os.path.exists(fname)
            new = fname.replace('RENAME', 'NEW')
            exp = "Would rename {} to {}".format(fname, new)
            assert exp in result


# -----------------------------------------------------------------------------
def test_rename_forreal(tmpdir, fx_rename):
    """
    Verify that 'fx rename' (no -n, --dryrun) behaves as expected
    """
    with chdir(tmpdir.strpath):
        cmd = "fx rename s/RENAME/NEW/ {}".format(" ".join(fx_rename))
        result = runcmd(cmd)
        assert result == ""
        for fname in fx_rename:
            assert not os.path.exists(fname)
            new = fname.replace('RENAME', 'NEW')
            assert os.path.exists(new)


# -----------------------------------------------------------------------------
def test_rename_verbose(tmpdir, fx_rename):
    """
    Verify that 'fx rename -v' behaves as expected
    """
    with chdir(tmpdir.strpath):
        cmd = "fx rename -v s/RENAME/NEW/ {}".format(" ".join(fx_rename))
        result = runcmd(cmd)
        for fname in fx_rename:
            new = fname.replace('RENAME', 'NEW')
            assert "Renaming {} to {}".format(fname, new) in result
            assert not os.path.exists(fname)
            assert os.path.exists(new)


# -----------------------------------------------------------------------------
def test_xargs_help():
    """
    Verify that the right stuff is in the output of 'fx help xargs'
    """
    cmd = "fx help xargs"
    result = runcmd(cmd)
    assert "(needs work)" not in result
    exp = ["Replace % in command with clumps of args",
           "-n, --dryrun     Report what would happen without acting",
           "-h, --help       Prints help information",
           "-v, --verbose    Report each command before running it",
           "<command>    String containing '%'",]
    for item in exp:
        assert item in result


# -----------------------------------------------------------------------------
def test_xargs_dryrun(tmpdir, fx_xargs):
    """
    Verify that 'fx xargs -n' behaves as expected
    """
    with chdir(tmpdir.strpath):
        cmd = "fx xargs -n \"echo foo % bar\""
        result = tbx.run(cmd, input="< tokens")
        with open("tokens", 'r') as inp:
            for line in inp:
                assert line.strip() in result
        for line in result.split("\r\n"):
            assert line.startswith("Would run 'echo foo ")
            assert line.strip().endswith(" bar'")


# -----------------------------------------------------------------------------
def test_xargs_norepl(tmpdir, fx_xargs):
    """
    If replstr does not appear in *command*, 'fx xargs' should complain
    """
    with chdir(tmpdir.strpath):
        cmd = "fx xargs 'echo command no repl'"
        result = tbx.run(cmd, input="< tokens")
        assert "No '%' found in 'echo command no repl'" in result






# -----------------------------------------------------------------------------
def test_xargs_forreal(tmpdir):
    """
    Verify that 'fx xargs' (no -n, --dryrun) behaves as expected
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_xargs_verbose(tmpdir):
    """
    Verify that 'fx rename -v' behaves as expected
    """
    pytest.fail('construction')


# -----------------------------------------------------------------------------
def test_deployable():
    """
    Check version against last git tag and check for untracked files or
    outstanding updates.
    """
    result = runcmd("git status --porc")

    # check for untracked files
    msg = "There are untracked files"
    assert "??" not in result, msg

    # check for unstaged updates
    msg = "There are unstaged updates"
    assert "\n M " not in result and "\n A " not in result, msg

    # check for staged but uncommitted changes
    msg = "There are staged but uncommitted updates"
    assert "\nM  " not in result and "\nA  " not in result, msg

    # check the current version against the most recent tag
    result = runcmd("git --no-pager tag")
    tag_l = result.strip().split("\r\n")
    if 0 < len(tag_l):
        latest_tag = tag_l[-1]
    else:
        latest_tag = ""

    assert latest_tag == current_version(), "Version does not match tag"

    # verify that the most recent tag points at HEAD
    cmd = "git --no-pager log -1 --format=format:\"%H\""
    tag_hash = runcmd(cmd + " {}".format(latest_tag))
    head_hash = runcmd(cmd)
    assert head_hash == tag_hash, "Tag != HEAD"


# -----------------------------------------------------------------------------
@contextlib.contextmanager
def chdir(directory):
    """
    Context-based directory excursion

    When the with statement ends, you're back where you started.
    """
    origin = os.getcwd()
    try:
        os.chdir(directory)
        yield

    finally:
        os.chdir(origin)


# -----------------------------------------------------------------------------
def current_version():
    """
    Determine the current project version by reading main.rs
    """
    with open("src/main.rs", 'r') as f:
        for line in itertools.takewhile(lambda line: "version() ->" not in line, f):
            pass
        vline = f.readline()
        return vline.strip("\" \r\n")


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_rename(tmpdir):
    """
    Set up files to be renamed by 'fx rename ...'
    """
    flist = ["RUNT_one_RENAME",
             "RUNT_two_RENAME_two",
             "RENAME_me_RUNT"]
    for fname in flist:
        tmpdir.join(fname).ensure()
    return flist


# -----------------------------------------------------------------------------
@pytest.fixture
def fx_xargs(tmpdir):
    """
    Write a file of arguments for 'fx xargs' to play with
    """
    with chdir(tmpdir.strpath):
        with open("tokens", 'w') as out:
            for idx in range(300):
                out.write("token_{:03d}\n".format(idx))


# -----------------------------------------------------------------------------
def runcmd(cmd):
    """
    Run a command and stringify and return stdout as the result
    """
    return pexpect.run(cmd).decode()
