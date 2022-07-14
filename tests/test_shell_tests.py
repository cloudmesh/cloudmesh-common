# ##############################################################
# pytest -v --capture=no tests/test_shell.py
# pytest -v  tests/test_shell.py
# pytest -v --capture=no  tests/test_shell.py::TestShell::<METHODNAME>
# ##############################################################


"""
This is the test for the new shell commands that we are implementing
for the purpose of making the workflow more easily synonymous with each of the
OS we have on the team.
"""
import os.path

# from cloudmesh.common.Shell import Shell
from cloudmesh.common.Shell import Shell as Shell
from cloudmesh.common.util import HEADING
from cloudmesh.common.Benchmark import Benchmark
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import Console
from pathlib import Path
from cloudmesh.common.systeminfo import os_is_windows, os_is_linux, os_is_mac

import time

class TestShell:

    # def test_fake_browser(self):
    #     browser = Shell.fake_browser
    #     HEADING()
    #     Benchmark.Start()
    #     # Shell.copy("test-graphviz.svg", '/tmp/test-graphviz.svg')
    #     # Shell.copy("test-graphviz.svg", "~/test-graphviz.svg")
    #     # r = Shell.browser("~/test-graphviz.svg")
    #     # Shell.copy("test-graphviz.svg", f"{Path.home()}/test-graphviz.svg")
    #     r = browser('http://google.com')
    #     assert '<title>Google</title>' in r
    #     # r = browser(f'https://google.com')
    #     # r = browser(
    #     #     f"C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
    #     # r = browser(
    #     #     f"file:///C:/Users/abeck/cm/cloudmesh-cc/test-graphviz.svg")
    #     # r = browser(f"~/test-graphviz.svg")
    #     # r = browser(f'test-graphviz.svg')
    #     # r = browser(f'./test-graphviz.svg')
    #     # assert r == path_expand(f'~/test-graphviz.svg')
    #     # input()
    #     # r = Shell.browser("file://~/test-graphviz.svg")
    #     # r = Shell.browser("test-graphviz.svg")
    #     # r = Shell.browser("file://test-graphviz.svg")
    #     # r = Shell.browser("file://tmp/test-graphviz.svg")
    #     # r = Shell.browser("http://google.com")
    #     # r = Shell.browser("https://google.com")
    #     Benchmark.Stop()

    def test_map_filename(self):
        HEADING()
        Benchmark.Start()
        user = os.path.basename(os.environ["HOME"])
        if os_is_windows():
            pwd = os.getcwd().replace("C:","/mnt/c").replace("\\","/")
        else:
            pwd = os.getcwd()

        print("pwd",pwd)

        ## wsl:~/dir         /mnt/c/Users/USER/dir
        # wsl:dir           /mnt/c/Users/USER/{PWD}/dir
        # wsl:./dir         /mnt/c/Users/USER/{PWD}/dir
        ## wsl:/mnt/c/Users  /mnt/c/Users
        # wsl:/dir          /dir

        result = Shell.map_filename(name='wsl:~/cm')
        assert result.user == user
        assert result.host == 'wsl'
        if os_is_linux():
            assert result.path == f'/mnt/c/home/{user}/cm'
        else:
            assert result.path == f'/mnt/c/Users/{user}/cm'

        result = Shell.map_filename(name='wsl:dir')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'{pwd}/dir'

        result = Shell.map_filename(name='wsl:./dir')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'{pwd}/dir'

        result = Shell.map_filename(name='wsl:/mnt/c/home')
        assert result.user == user
        assert result.host == 'wsl'
        assert result.path == f'/mnt/c/home'

        result = Shell.map_filename(name='C:~/cm')
        assert result.user == user
        assert result.host == 'localhost'
        if os_is_linux():
            if user == 'root':
                assert result.path == f'C:\\root\\cm'
            else:
                assert result.path == f'C:\\home\\{user}\\cm'
        else:
            assert result.path == f'C:\\Users\\{user}\\cm'

        result = Shell.map_filename(name='scp:user@host:~/cm')
        assert result.user == "user"
        assert result.host == 'host'
        assert result.path == f'~/cm'

        result = Shell.map_filename(name='scp:user@host:/tmp')
        assert result.user == "user"
        assert result.host == 'host'
        assert result.path == f'/tmp'

        result = Shell.map_filename(name='~/cm')
        assert result.user == user
        assert result.host == 'localhost'
        assert result.path == path_expand('~/cm')

        result = Shell.map_filename(name='/tmp')
        assert result.user == user
        assert result.host == 'localhost'
        if os_is_windows():
            assert result.path == '\\tmp'
        else:
            assert result.path == '/tmp'

        result = Shell.map_filename(name='./cm')
        assert result.user == user
        assert result.host == 'localhost'
        assert result.path == path_expand('./cm')
        Benchmark.Stop()

    def test_open(self):
        HEADING()
        Benchmark.Start()
        r = Shell.open('test-dot.svg')
        r2 = Shell.open('~/cm/cloudmesh-cc/test-dot.svg')
        if os_is_windows():
            assert 'command not found' and 'cannot find the file' not in r
            assert 'command not found' and 'cannot find the file' not in r2
            print('a')
        if os_is_linux():
            assert 'command not found' and 'cannot find the file' not in r
            assert 'command not found' and 'cannot find the file' not in r2
            print('b')
        if os_is_mac():
            assert 'command not found' and 'cannot find the file' and 'Unable to find application' not in r
            assert 'command not found' and 'cannot find the file' and 'Unable to find application' not in r2
            r3 = Shell.open('test-dot.svg', program='Google Chrome')
            assert 'command not found' and 'cannot find the file' and 'Unable to find application' not in r2

            print('c')

        Benchmark.Stop()

    def test_shell_head(self):
        HEADING()
        Benchmark.Start()
        r = Shell.head('requirements.txt')
        Benchmark.Stop()
        print(r)
        assert 'docker-composse' not in r
        assert 'psutil' in r
        assert '#' in r
        assert 'starlette' not in r
        r = Shell.head('requirements.txt', lines=1)
        print('----')
        print(r)
        assert '#' in r
        assert 'cloudmesh-sys' not in r

    def test_shell_tail(self):
        HEADING()
        Benchmark.Start()
        r = Shell.tail('requirements.txt')
        Benchmark.Stop()
        print(r)
        assert 'cloudmesh-sys' not in r
        assert '#' not in r
        assert 'requests' in r
        assert 'cloudmesh-cmd5' not in r
        r = Shell.tail('requirements.txt', lines=1)
        print('----')
        print(r)
        assert 'tqdm' in r
        assert 'cloudmesh-sys' not in r

    def test_shell_cat(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.cat(file)
        Benchmark.Stop()
        assert 'requests' in r
        assert 'psutil' in r
        assert 'docker-compose' not in r
        assert '#' in r

    def test_shell_ping(self):
        HEADING()
        Benchmark.Start()
        host = 'www.google.com'
        r = Shell.ping(host)
        print(r)
        Benchmark.Stop()
        if 'not found' in r:
            Console.error('ping not installed')
            assert False
        assert 'Packets' or 'packets' in r
        assert 'www.google.com' in r
        assert 'time=' in r

    def test_shell_rm(self):
        HEADING()
        user_dir = Path.home()
        user_dir = os.path.join(user_dir, 'delete-test-file')
        Benchmark.Start()
        os.system('touch psuedo-directory')
        r = Shell.rm('psuedo-directory')
        os.system(f'touch {user_dir}')
        r = Shell.rm('~/delete-test-file')
        Benchmark.Stop()
        assert not os.path.exists(path_expand('psuedo-directory'))
        assert not os.path.exists(path_expand('~/delete-test-file'))

    def test_shell_fgrep(self):
        HEADING()
        Benchmark.Start()
        file = path_expand('requirements.txt')
        r = Shell.fgrep('requests', file)
        Benchmark.Stop()
        assert 'requests' in r

    def test_shell_grep(self):
        HEADING()
        Benchmark.Start()

        Benchmark.Stop()

    def test_shell_which(self):
        HEADING()
        Benchmark.Start()

        Benchmark.Stop()

    def test_shell_mkdir(self):
        HEADING()

        os.system('rm -rf shell-directory')
        os.system('rm -rf shell-new-dir/another-dir')
        os.system('rm -rf ~/shell-dir')
        Benchmark.Start()
        Shell.mkdir('shell-directory')
        assert os.path.exists('shell-directory')
        Shell.mkdir('shell-new-dir/another-dir')
        assert os.path.exists('shell-new-dir/another-dir')
        Shell.mkdir('~/shell-dir')
        dir = os.path.join(Path.home(), 'shell-dir')
        assert os.path.exists(dir)
        Benchmark.Stop()
        os.system('rm -rf shell-directory')
        os.system('rm -rf shell-new-dir/another-dir')
        os.system('rm -rf ~/shell-dir')

    def test_shell_browser(self):
        HEADING()
        Benchmark.Start()
        cwd = os.getcwd()
        # Shell.copy("test-graphviz.svg", '/tmp/test-graphviz.svg')
        # Shell.copy("test-graphviz.svg", "~/test-graphviz.svg")
        # r = Shell.browser("~/test-graphviz.svg")
        # Shell.copy("test-graphviz.svg", f"{Path.home()}/test-graphviz.svg")
        r = Shell.browser(f'https://google.com')
        r = Shell.browser(f"{cwd}/tests/test.svg")
        r = Shell.browser(f"file:///{cwd}/tests/test.svg")
        # r = Shell.browser(f"~/cm/cloudmesh-cc/test.svg")
        # r = Shell.browser(f'tests/test.svg')
        r = Shell.browser(f'./tests/test.svg')
        # assert r == path_expand(f'~/test-graphviz.svg')
        # input()
        # r = Shell.browser("file://~/test-graphviz.svg")
        # r = Shell.browser("file://test-graphviz.svg")
        # r = Shell.browser("file://tmp/test-graphviz.svg")
        print(r)
        Benchmark.Stop()

    def test_shell_copy(self):
        HEADING()
        Shell.mkdir('shell-directory')
        Benchmark.Start()
        r = Shell.copy(f'requirements.txt', f'shell-directory')
        r = Shell.copy(f'requirements.txt', f'requirements2.txt')
        r = Shell.copy(f'requirements.txt', f'shell-directory/test.txt')
        Benchmark.Stop()
        assert os.path.exists(path_expand(f'shell-directory/requirements.txt'))
        assert os.path.exists(path_expand(f'requirements2.txt'))
        assert os.path.exists(path_expand(f'shell-directory/test.txt'))
        os.system('rm -rf shell-directory')
        os.system('rm requirements2.txt')

    # def test_shell_sync(self):
    #     HEADING()
    #     Benchmark.Start()
    #     file = path_expand('requirements.txt')
    #     r = Shell.rsync(file)
    #     Benchmark.Stop()


