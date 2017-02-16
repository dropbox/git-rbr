# Usage:
# $ py.test

import os.path
import pytest
import re
import shutil
import subprocess
from subprocess import check_output, check_call
import tempfile


@pytest.fixture
def repo():
    # type: () -> str
    d = tempfile.mkdtemp()
    git_dir = os.environ.get('GIT_DIR')
    os.environ['GIT_DIR'] = os.path.join(d, '.git')
    cwd = os.getcwd()
    os.chdir(d)
    check_call(['git', 'init', d])

    print d
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
    try:
        check_output(['sh', '-exc', cmds])
    except subprocess.CalledProcessError as e:
        cmds_fmtd = re.sub('^', '  ', cmds.strip('\n'), flags=re.M) + '\n'
        raise RuntimeError('Shell commands exited with code %s:\n%s'
                           % (e.returncode, cmds_fmtd))


def expect_conflict(cmd):
    # type: (str) -> None
    '''Expect `cmd` to fail with a conflict message.'''
    try:
        out = check_output(cmd, stderr=subprocess.STDOUT)
        print out
        raise RuntimeError('Expected conflict; none happened')
    except subprocess.CalledProcessError as e:
        if 'git rbr --continue' not in e.output:
            print e.output
            raise RuntimeError('Expected conflict; got different message')


def setup_shell(cmds):
    # type: (str) -> None
    preamble = '''
testci () {
  # args: message [filename [contents]]
  # optional args default to message
  mkdir -p "$(dirname "${2:-$1}")" &&
  echo "${3:-$1}" >"${2:-$1}" &&
  git add "${2:-$1}" &&
  git commit -m "$1"
}
'''
    shell(preamble + cmds)


def subjects_between(upstream, branch):
    return check_output(['git', 'log', '--pretty=format:%s', '--reverse',
                         '%s..%s' % (upstream, branch)]).strip('\n').split('\n')


def assert_atop(upstream, branch):
    assert '0' == check_output(
        ['git', 'rev-list', '--count', '--max-count=1',
         upstream, '--not', branch, '--']).strip()


def assert_updated(branches=None):
    '''Assert each branch is atop its upstream.  If None, all branches but master.'''
    if branches is None:
        all_branches = set(check_output(
            ['git', 'for-each-ref', '--format=%(refname:short)', 'refs/heads/']
        ).strip().split('\n'))
        branches = all_branches - set(['master'])

    for branch in branches:
        assert_atop(branch+'@{u}', branch)


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
    assert ' '.join(subjects_between('master^', 'c')) == 'master2 a a2 b b2 c'


def test_fork(repo):
    # master <- a <- b
    #             <- c
    # each advanced, no conflicts
    setup_shell('''
testci master
git checkout -tb a
testci a
git checkout -tb b
testci b
git checkout a -tb c
testci c
git checkout master
testci master2
git checkout a
testci a2
''')
    check_call(['git', 'rbr', '-v'])
    assert_updated()


@pytest.fixture
def repo_conflicted(repo):
    # master -> a -> b -> ab -> c
    # master, a advanced
    # a, ab conflict
    setup_shell('''
testci master
git checkout -tb a
testci a
git checkout -tb b
testci b
git checkout -tb ab
testci ab a
git checkout -tb c
testci c
git checkout master
testci master2
git checkout a
testci aa a
''')


def test_continue(repo_conflicted):
    setup_shell('git checkout a')
    expect_conflict(['git', 'rbr', '-v'])
    check_call(['git', 'add', '-u'])
    check_call(['git', 'rbr', '--continue'])
    assert_updated()
    assert ' '.join(subjects_between('master^', 'c')) == 'master2 a aa b ab c'


def test_skip(repo_conflicted):
    setup_shell('git checkout a')
    expect_conflict(['git', 'rbr', '-v'])
    check_call(['git', 'rbr', '--skip'])
    assert_updated()
    assert ' '.join(subjects_between('master^', 'c')) == 'master2 a aa b c'


def test_abort(repo_conflicted):
    setup_shell('git checkout a')
    # TODO WORK HERE
