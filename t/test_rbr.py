# Usage:
# $ py.test

import os.path
import pytest
import shutil
import subprocess
from subprocess import check_output, check_call
import tempfile


@pytest.fixture
def repo():
    # type: () -> str
    d = tempfile.mkdtemp()
    check_output(['git', 'init', d])
    git_dir = os.environ.get('GIT_DIR')
    os.environ['GIT_DIR'] = os.path.join(d, '.git')
    cwd = os.getcwd()
    os.chdir(d)

    return d

    # Pytest 2.6.1 which I have handy doesn't support this.  Forget it for now.
    # yield d

    os.chdir(cwd)
    if git_dir is None:
        del os.environ['GIT_DIR']
    else:
        os.environ['GIT_DIR'] = git_dir
    shutil.rmtree(d)


def shell(cmds):
    # type: (str) -> None
    check_output(['sh', '-c', cmds])


def setup_shell(cmds):
    # type: (str) -> None
    preamble = '''
testci () { mkdir -p "$(dirname "$1")" && echo "$1" >"$1" && git add "$1" && git commit -m "$1"; }
'''
    shell(preamble + cmds)


def assert_updated(branches=None):
    '''Assert each branch is atop its upstream.  If None, all branches but master.'''
    if branches is None:
        all_branches = set(check_output(
            ['git', 'for-each-ref', '--format=%(refname:short)', 'refs/heads/']
        ).strip().split('\n'))
        branches = all_branches - set(['master'])

    for branch in branches:
        assert '0' == check_output(
            ['git', 'rev-list', '--count', '--max-count=1',
             branch+'@{u}', '--not', branch, '--']).strip()


def test_simple(repo):
    # master <- a <- b <- c, each advanced, no conflicts
    setup_shell('''
testci master
git checkout -tb a
testci a
git checkout -tb b
testci b
git checkout -tb c
testci c
git checkout master
testci master2
git checkout a
testci a2
git checkout b
testci b2
git checkout a
''')
    check_call(['git', 'rbr', '-v'])
    assert_updated()
