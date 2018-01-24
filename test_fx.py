import itertools
import pdb
import pexpect
import pytest

# -----------------------------------------------------------------------------
def test_cargo_test():
    """
    Run 'cargo test' and verify its output reflects all tests passing
    """
    result = runcmd("cargo test")
    assert "panic" not in result
    assert "error" not in result


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
def runcmd(cmd):
    """
    Run a command and stringify and return stdout as the result
    """
    return pexpect.run(cmd).decode()
