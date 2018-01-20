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
def test_cmd_supports_dryrun_before():
    """
    Verify that 'fx cmd' supports -n before the command
    """
    cmd = "fx cmd --dryrun \"echo foo % bar\" one two three"
    result = pexpect.run(cmd).decode()
    exp = "".join(["would do 'echo foo {} bar'\r\n".format(x)
                   for x in ["one", "two", "three"]])
    assert exp == result


# -----------------------------------------------------------------------------
def test_cmd_supports_dryrun_after():
def test_cmd_dryrun_verbose_optional():
    """
    Verify that 'fx cmd' supports -n after the command
    """
    cmd = "fx cmd \"echo foo % bar\" one two three --dryrun"
    result = pexpect.run(cmd).decode()
    exp = "".join(["would do 'echo foo {} bar'\r\n".format(x)
                   for x in ["one", "two", "three"]])
    assert exp == result


# -----------------------------------------------------------------------------
def test_cmd_supports_n_before():
@pytest.mark.parametrize("cmd", [
    "fx cmd \"echo foo % bar\" one two three -v",
    "fx cmd \"echo foo % bar\" one two three --verbose",
    "fx cmd -v \"echo foo % bar\" one two three",
    "fx cmd --verbose \"echo foo % bar\" one two three",
    ])
def test_cmd_verbose_supported(cmd):
    """
    Verify that 'fx cmd' supports -n before the command
    Verify that 'fx cmd' supports the verbose option in various positions
    """
    cmd = "fx cmd -n \"echo foo % bar\" one two three"
    result = pexpect.run(cmd).decode()
    exp = "".join(["would do 'echo foo {} bar'\r\n".format(x)
                   for x in ["one", "two", "three"]])
    assert exp == result
    result = runcmd(cmd)
    arglist = ["one", "two", "three"]
    body = "> echo foo {0} bar\r\nfoo {0} bar\r\n"
    exp = "".join([body.format(x) for x in arglist])
    assert result == exp


# -----------------------------------------------------------------------------
def test_cmd_supports_n_after():
    """
    Verify that 'fx cmd' supports -n after the command
    """
    cmd = "fx cmd \"echo foo % bar\" one two three -n"
    result = pexpect.run(cmd).decode()
    exp = "".join(["would do 'echo foo {} bar'\r\n".format(x)
                   for x in ["one", "two", "three"]])
    assert exp == result

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
def test_zpad_not_required():
    """
    Run 'fx range' without the -z / --zpad option to verify it's not required
    """
    cmd = "fx range \"echo foo % bar\" -i 10..15"
    result = pexpect.run(cmd).decode()
    exp = "".join(["foo {} bar\r\n".format(x) for x in range(10, 15)])
    assert exp == result
    

# -----------------------------------------------------------------------------
def test_z_supported_after():
    """
    Run 'fx range' without the -z / --zpad option to verify it's not required
    """
    cmd = "fx range \"echo foo % bar\" -i 10..15 -z 3"
    result = pexpect.run(cmd).decode()
    exp = "".join(["foo {:03d} bar\r\n".format(x) for x in range(10, 15)])
    assert exp == result


# -----------------------------------------------------------------------------
def test_z_supported_before():
    """
    Run 'fx range' without the -z / --zpad option to verify it's not required
    """
    cmd = "fx range -z 4 \"echo foo % bar\" -i 10..15"
    result = pexpect.run(cmd).decode()
    exp = "".join(["foo {:04d} bar\r\n".format(x) for x in range(10, 15)])
    assert exp == result

# -----------------------------------------------------------------------------
def test_zpad_supported_after():
    """
    Run 'fx range' without the -z / --zpad option to verify it's not required
    """
    cmd = "fx range \"echo foo % bar\" -i 10..15 --zpad 5"
    result = pexpect.run(cmd).decode()
    exp = "".join(["foo {:05d} bar\r\n".format(x) for x in range(10, 15)])
    assert exp == result


# -----------------------------------------------------------------------------
def test_zpad_supported_before():
    """
    Run 'fx range' without the -z / --zpad option to verify it's not required
    """
    cmd = "fx range --zpad 6 \"echo foo % bar\" -i 10..15"
    result = pexpect.run(cmd).decode()
    exp = "".join(["foo {:06d} bar\r\n".format(x) for x in range(10, 15)])
    assert exp == result

