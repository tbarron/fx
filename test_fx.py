import pexpect
import pytest

# -----------------------------------------------------------------------------
def test_cargo_test():
    """
    Run 'cargo test' and verify its output reflects all tests passing
    """
    result = pexpect.run("cargo test").decode()
    assert "panic" not in result


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
def test_cmd_dryrun_verbose_optional():
    """
    Verify that 'fx cmd' makes dryrun optional
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
    result = runcmd(cmd)
    exp = "".join([xbody.format(x) for x in range(10, 15)])
    assert result == exp


# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
    """
    Run 'fx range' without the -z / --zpad option to verify it's not required
    """
    result = pexpect.run(cmd).decode()


# -----------------------------------------------------------------------------
    """
    """
