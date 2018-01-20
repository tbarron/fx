import pexpect
import pytest

# -----------------------------------------------------------------------------
def test_cargo_test():
    """
    Run 'cargo test' and verify its output reflects all tests passing
    """
    result = runcmd("cargo test")
    assert "panic" not in result


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
    exp = ["error: The following required arguments were not provided",
           "<command>",
           "--interval <interval>",
           "<items>",
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
    exp = ["error: The following required arguments were not provided",
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
def runcmd(cmd):
    """
    Run a command and stringify and return stdout as the result
    """
    return pexpect.run(cmd).decode()
