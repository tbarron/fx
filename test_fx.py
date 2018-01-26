import contextlib
import glob
import itertools
import os
import pdb
import pexpect
import py
import pytest
import re
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
           "cmd       Replace <replstr> with arguments",
           "help      Prints this message or the help of the given "
           "subcommand(s)",
           "mag       Report the size of a number",
           "odx       Report hex, decimal, octal, and binary values",
           "perrno    Report errno values and meanings",
           "range     Replace <replstr> with <interval> values and "
           "run the commands",
           "rename    Rename files based on a s/foo/bar/ expr",
           "xargs     Replace <replstr> in command with clumps of arguments",
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
def test_cmd_help():
    """
    Verify that the right stuff is in the output of 'fx help cmd'
    """
    cmd = "fx help cmd"
    result = runcmd(cmd)
    exp = ["Replace <replstr> with arguments and run the commands",
           "-n, --dryrun     Report what would happen without acting",
           "-r, --replstr <replstr>    Alternate replacement substring in "
           "command (default: '%')",
           "-h, --help       Prints help information",
           "-v, --verbose    Show command before running it",
           "<command>     Command string containing <replstr>",
           "<items>...    <replstr> replacements",
           ]
    unexp = ["(needs work)"]
    for item in exp:
        assert item in result
    for item in unexp:
        assert item not in result


# -----------------------------------------------------------------------------
def test_cmd_command_norepl_def():
    """
    Verify that if command doesn't contain default <replstr> 'fx cmd' complains
    """
    fx_cmd = "echo this is the command with no replstr"
    cmd = "fx cmd \"{}\" one two three".format(fx_cmd)
    result = runcmd(cmd)
    assert result.strip() == "No '%' found in '{}'".format(fx_cmd)


# -----------------------------------------------------------------------------
def test_cmd_command_norepl_alt():
    """
    Verify that if command doesn't contain alternate <replstr> 'fx cmd'
    complains
    """
    fx_cmd = "echo this is the command with no replstr"
    cmd = "fx cmd -r zzz \"{}\" one two three".format(fx_cmd)
    result = runcmd(cmd)
    assert result.strip() == "No 'zzz' found in '{}'".format(fx_cmd)


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
           "fx cmd [FLAGS] [OPTIONS] <command> <items>...",
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
           "fx cmd [FLAGS] [OPTIONS] <command> <items>...",
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
    exp = "".join(["Would run 'echo foo {} bar'\r\n".format(x)
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
    "fx cmd -r xxx \"echo foo xxx bar\" one two three -v",
    "fx cmd -r xxx \"echo foo xxx bar\" one two three --verbose",
    "fx cmd -r xxx -v \"echo foo xxx bar\" one two three",
    "fx cmd -r xxx --verbose \"echo foo xxx bar\" one two three",
    ])
def test_cmd_altrepl_supported(cmd):
    """
    Verify that 'fx cmd' works with an alternate replstr
    """
    result = runcmd(cmd)
    arglist = ["one", "two", "three"]
    body = "> echo foo {0} bar\r\nfoo {0} bar\r\n"
    exp = "".join([body.format(x) for x in arglist])
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
@pytest.mark.parametrize("cmd", [
    "fx range -r xxx \"echo foo xxx bar\" -i 1..5 -v",
    "fx range -r xxx \"echo foo xxx bar\" -i 1..5 --verbose",
    "fx range -r xxx -v \"echo foo xxx bar\" -i 1..5",
    "fx range -r xxx --verbose \"echo foo xxx bar\" -i 1..5",
    ])
def test_range_altrepl_supported(cmd):
    """
    Verify that 'fx cmd' works with an alternate replstr
    """
    result = runcmd(cmd)
    arglist = [1, 2, 3, 4]
    body = "> echo foo {0} bar\r\nfoo {0} bar\r\n"
    exp = "".join([body.format(x) for x in arglist])
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
def test_range_help():
    """
    Verify that the right stuff is in the output of 'fx help range'
    """
    cmd = "fx help range"
    result = runcmd(cmd)
    exp = ["Replace <replstr> with <interval> values and run the commands",
           "-n, --dryrun     Report what would happen without acting",
           "-r, --replstr <replstr>      Alternate replacement substring in "
           "command (default: '%')",
           "-h, --help       Prints help information",
           "-v, --verbose    Show command before running it",
           "-i, --interval <interval>    <low>..<high> range from "
           "<low> to <high>-1",
           "-z, --zpad <zeropad>         Zero fill to <zeropad> columns",
           "<command>    Command string containing <replstr>",
           ]
    unexp = ["(needs work)"]
    for item in exp:
        assert item in result
    for item in unexp:
        assert item not in result


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
@pytest.mark.parametrize("cmd", [
    "fx range \"echo foo % bar\" -i 1..5 --dryrun",
    "fx range --dryrun \"echo foo % bar\" -i 1..5",
    "fx range \"echo foo % bar\" -i 1..5 -n",
    "fx range -n \"echo foo % bar\" -i 1..5",
    ])
def test_range_dryrun_supported(cmd):
    """
    Verify that 'fx cmd' supports the dryrun option in various positions
    """
    result = runcmd(cmd)
    exp = "".join(["Would run 'echo foo {} bar'\r\n".format(x)
                   for x in [1, 2, 3, 4]])
    assert result == exp


# -----------------------------------------------------------------------------
@pytest.mark.parametrize("cmd, xbody", [
    ("fx range \"echo foo % bar\" -i 10..15 -z 3", "foo {:03d} bar\r\n"),
    ("fx range -z 4 \"echo foo % bar\" -i 10..15", "foo {:04d} bar\r\n"),
    ("fx range \"echo foo % bar\" -i 10..15 --zpad 5", "foo {:05d} bar\r\n"),
    ("fx range --zpad 6 \"echo foo % bar\" -i 10..15", "foo {:06d} bar\r\n"),
    ("fx range \"echo foo % bar\" -i 10..15 -v",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ("fx range -v \"echo foo % bar\" -i 10..15",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ("fx range \"echo foo % bar\" -i 10..15 --verbose",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ("fx range --verbose \"echo foo % bar\" -i 10..15",
     "> echo foo {0} bar\r\nfoo {0} bar\r\n"),
    ])
def test_range_zpad_supported(cmd, xbody):
def test_range_verbose_supported(cmd, xbody):
    """
    Verify that option -z/--zpad is supported in various positions
    Verify that -v/--verbose is supported on 'fx range' in various positions
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
    exp = ["Replace <replstr> in command with clumps of arguments",
           "-n, --dryrun     Report what would happen without acting",
           "-r, --replstr <replstr>    Alternate replacement substring in "
           "command (default: '%')",
           "-h, --help       Prints help information",
           "-v, --verbose    Show command before running it",
           "<command>    Command string containing <replstr>",]
    unexp = ["(needs work)"]
    for item in exp:
        assert item in result
    for item in unexp:
        assert item not in result


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
def test_xargs_altnorepl(tmpdir, fx_xargs):
    """
    'fx xargs --replstr foo' should use 'foo' rather than '%' as the replstr
    but should complain about the fact that 'foo' does not appear in the
    command
    """
    with chdir(tmpdir.strpath):
        cmd = "fx xargs -n -r foo 'echo The juice is >>>here<<<'"
        result = tbx.run(cmd, input="< tokens")
        assert "No 'foo' found in 'echo The juice is >>>here<<<'" in result


# -----------------------------------------------------------------------------
def test_xargs_altrepl(tmpdir, fx_xargs):
    """
    'fx xargs --replstr foo' should use 'foo' rather than '%' as the replstr
    """
    with chdir(tmpdir.strpath):
        cmd = "fx xargs -n -r here 'echo The juice is >>>here<<<'"
        result = tbx.run(cmd, input="< tokens")
        with open("tokens", 'r') as inp:
            for line in inp:
                assert line.strip() in result
        for line in result.split("\r\n"):
            assert line.startswith("Would run 'echo The ")
            assert line.strip().endswith("<<<'")


# -----------------------------------------------------------------------------
def test_xargs_forreal(tmpdir, fx_xargs):
    """
    Verify that 'fx xargs' (no -n, --dryrun) behaves as expected
    """
    with chdir(tmpdir.strpath):
        cmd = "fx xargs 'touch first % last'"
        result = tbx.run(cmd, input="< tokens")
        assert "Would run" not in result
        assert "Running" not in result
        with open("tokens", 'r') as inp:
            for line in inp:
                fobj = py.path.local(line.strip())
                assert fobj.exists()
        assert py.path.local("first").exists()
        assert py.path.local("last").exists()


# -----------------------------------------------------------------------------
def test_xargs_verbose(tmpdir, fx_xargs):
    """
    Verify that 'fx rename -v' behaves as expected
    """
    with chdir(tmpdir.strpath):
        cmd = "fx xargs -v 'touch first % last'"
        result = tbx.run(cmd, input="< tokens")
        assert "Would run" not in result
        assert "Running" in result
        with open("tokens", 'r') as inp:
            for line in inp:
                fobj = py.path.local(line.strip())
                assert fobj.exists()
        assert py.path.local("first").exists()
        assert py.path.local("last").exists()


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

    # check for unstaged updates or staged but uncommitted updates
    msg = "There are uncommitted updates, staged or unstaged"
    assert not re.findall("\n?(MM|MA|AM|AA|A |M | A| M)", result), msg

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


# -----------------------------------------------------------------------------
def younger_than(first, second):
    """
    Return True if *first* has a more recent mtime than *second*
    """
    first_p = py.path.local(first)
    second_p = py.path.local(second)
    return second_p.mtime() < first_p.mtime()


# -----------------------------------------------------------------------------
