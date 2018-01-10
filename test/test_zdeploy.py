import pytest
skip_deployable = False
try:
    from git import Repo
except ImportError:
    skip_deployable = True


# -----------------------------------------------------------------------------
def test_deployable():
    """
    Check current version against last git tag and check for outstanding
    untracked files
    """
    if skip_deployable:
        pytest.skip()
    r = Repo('.')
    assert [] == r.untracked_files, "You have untracked files"
    assert [] == r.index.diff(r.head.commit), "You have staged updates"
    assert [] == r.index.diff(None), "You have uncommited changes"

    stags = sorted(r.tags,
                   key=lambda x: x.commit.committed_date,
                   reverse=True)

    assert version.__version__ == str(stags[0]), "Version does not match tag"

    assert str(r.head.commit) == str(stags[0].commit), "Tag != HEAD"
