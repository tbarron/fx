from fx import version
import pytest
import tbx


# -----------------------------------------------------------------------------
def test_deployable():
    """
    Check current version against last git tag and check for outstanding
    untracked files
    """
    pytest.dbgfunc()
    staged, changed, untracked = tbx.git_status()
    assert untracked == [], "You have untracked files"
    assert changed == [], "You have unstaged updates"
    assert staged == [], "You have updates staged but not committed"

    if tbx.git_current_branch() != 'master':
        return True

    last_tag = tbx.git_last_tag()
    msg = "Version ({}) does not match tag ({})".format(tbx.version(),
                                                        last_tag)
    assert version() == last_tag, msg
    assert tbx.git_hash() == tbx.git_hash(last_tag), "Tag != HEAD"
