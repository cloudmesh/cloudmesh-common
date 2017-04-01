"""
A convenient method to execute shell commands and return their output. Note: that thsi method requires that the 
command be completley execute before the output is returned. FOr many activities in cloudemsh this is sufficient.
"""

from __future__ import print_function

import errno
import glob
import os
import os.path
import platform
import subprocess
import zipfile
from pipes import quote

from cloudmesh.common.console import Console


# from cloudmesh.common.util import path_expand

def path_expand(text):
    """ returns a string with expanded variable.

    :param text: the path to be expanded, which can include ~ and $ variables
    :param text: string

    """
    template = Template(text)
    result = template.substitute(os.environ)
    result = os.path.expanduser(result)
    return result


class SubprocessError(Exception):
    """
    Manages the formatting of the error and stdout. 
    THis command should not be directly called. Instead use SHell
    """
    def __init__(self, cmd, returncode, stderr, stdout):
        """
        sets the error
        :param cmd: the command executed
        :param returncode: the return code
        :param stderr: the stderr
        :param stdout: the stdout
        """
        self.cmd = cmd
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout

    def __str__(self):

        def indent(lines, amount, ch=' '):
            """
            indent the lines by multiples of ch
            :param lines: 
            :param amount: 
            :param ch: 
            :return: 
            """
            padding = amount * ch
            return padding + ('\n' + padding).join(lines.split('\n'))

        cmd = ' '.join(map(quote, self.cmd))
        s = ''
        s += 'Command: %s\n' % cmd
        s += 'Exit code: %s\n' % self.returncode

        if self.stderr:
            s += 'Stderr:\n' + indent(self.stderr, 4)
        if self.stdout:
            s += 'Stdout:\n' + indent(self.stdout, 4)

        return s


class Subprocess(object):
    """
    Executes a command. This class should not be directly used, but instead you should use Shell.
    """
    def __init__(self, cmd, cwd=None, stderr=subprocess.PIPE, stdout=subprocess.PIPE, env=None):
        """
        execute the given command
        :param cmd: the command
        :param cwd: the directory in which to execute the command
        :param stderr: the pipe for stderror
        :param stdout: the pipe for the stdoutput
        :param env: 
        """
        Console.debug_msg('Running cmd: {}'.format(' '.join(map(quote, cmd))))

        proc = subprocess.Popen(cmd, stderr=stderr, stdout=stdout, cwd=cwd, env=env)
        stdout, stderr = proc.communicate()

        self.returncode = proc.returncode
        self.stderr = stderr
        self.stdout = stdout

        if self.returncode != 0:
            raise SubprocessError(cmd, self.returncode, self.stderr, self.stdout)


class Shell(object):
    """
    The shell class allowing us to conveniently access many operating system commands. 
    TODO: This works well on Linux and OSX, but has not been tested much on WIndows
    """

    # TODO: we have not supported cygwin for a while
    cygwin_path = 'bin'  # i copied fom C:\cygwin\bin

    command = {
        'windows': {},
        'linux': {},
        'darwin': {}
    }

    '''

    big question for badi and others

    how do we now define dynamically functions based on a list that we want to support

    what we want is where args are multiple unlimited parameters to the function

    def f(args...):
        name = get the name from f
        a = list of args...

        cls.execute(cmd, arguments=a, capture=True, verbose=False)

    commands = ['ps', 'ls', ..... ]
    for c in commands:
        generate this command and add to this class dynamically

    or do something more simple

    ls = cls.execute('cmd', args...)

    '''

    @classmethod
    def check_output(cls, *args, **kwargs):
        """Thin wrapper around :func:`subprocess.check_output`
        """
        return subprocess.check_output(*args, **kwargs)

    @classmethod
    def ls(cls, *args):
        """
        executes ls with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('ls', args)

    @classmethod
    def ps(cls, *args):
        """
        executes ps with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('ps', args)

    @classmethod
    def bash(cls, *args):
        """
        executes bash with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('bash', args)

    @classmethod
    def cat(cls, *args):
        """
        executes cat with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('cat', args)

    @classmethod
    def git(cls, *args):
        """
        executes git with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('git', args)

    # noinspection PyPep8Naming
    @classmethod
    def VBoxManage(cls, *args):
        """
        executes VboxManage with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('VBoxManage', args)

    @classmethod
    def blockdiag(cls, *args):
        """
        executes blockdiag with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('blockdiag', args)

    @classmethod
    def cm(cls, *args):
        """
        executes cm with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('cm', args)

    @classmethod
    def fgrep(cls, *args):
        """
        executes fgrep with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('fgrep', args)

    @classmethod
    def grep(cls, *args):
        """
        executes grep with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('grep', args)

    @classmethod
    def head(cls, *args):
        """
        executes head with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('head', args)

    @classmethod
    def keystone(cls, *args):
        """
        executes keystone with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('keystone', args)

    @classmethod
    def kill(cls, *args):
        """
        executes kill with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('kill', args)

    @classmethod
    def nosetests(cls, *args):
        """
        executes nosetests with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('nosetests', args)

    @classmethod
    def nova(cls, *args):
        """
        executes nova with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('nova', args)

    @classmethod
    def ping(cls, host=None, count=1):
        """
        execute ping
        :param host: the host to ping 
        :param count: the number of pings
        :return: 
        """
        return cls.execute('ping', "-c {} {}".format(count, host))

    @classmethod
    def pwd(cls, *args):
        """
        executes pwd with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('pwd', args)

    @classmethod
    def rackdiag(cls, *args):
        """
        executes rackdiag with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('rackdiag', args)

    @classmethod
    def rm(cls, *args):
        """
        executes rm with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('rm', args)

    @classmethod
    def rsync(cls, *args):
        """
        executes rsync with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('rsync', args)

    @classmethod
    def scp(cls, *args):
        """
        executes scp with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('scp', args)

    @classmethod
    def sort(cls, *args):
        """
        executes sort with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('sort', args)

    @classmethod
    def sh(cls, *args):
        """
        executes sh with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('sh', args)

    @classmethod
    def ssh(cls, *args):
        """
        executes ssh with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('ssh', args)

    @classmethod
    def sudo(cls, *args):
        """
        executes sudo with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('sudo', args)

    @classmethod
    def tail(cls, *args):
        """
        executes tail with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('tail', args)

    @classmethod
    def vagrant(cls, *args):
        """
        executes vagrant with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('vagrant', args)

    @classmethod
    def mongod(cls, *args):
        """
        executes mongod with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('mongod', args)


    @classmethod
    def dialog(cls, *args):
        """
        executes dialof with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('dialog', args)

    @classmethod
    def pip(cls, *args):
        """
        executes pip with the given arguments
        :param args: 
        :return: 
        """
        return cls.execute('pip', args)

    @classmethod
    def remove_line_with(cls, lines, what):
        """
        returns all lines that do not contain what
        :param lines: 
        :param what: 
        :return: 
        """
        result = []
        for line in lines:
            if what not in line:
                result = result + [line]
        return result

    @classmethod
    def find_lines_with(cls, lines, what):
        """
        returns all lines that contain what
        :param lines: 
        :param what: 
        :return: 
        """
        result = []
        for line in lines:
            if what in line:
                result = result + [line]
        return result

    def __init__(cls):
        """
        identifies parameters for the os
        """
        if cls.operating_system() == "windows":
            cls.find_cygwin_executables()
        else:
            pass
            # implement for cmd, for linux we can just pass as it includes everything

    @classmethod
    def find_cygwin_executables(cls):
        """
        find the executables in cygwin
        """
        exe_paths = glob.glob(cls.cygwin_path + r'\*.exe')
        # print cls.cygwin_path
        # list all *.exe in  cygwin path, use glob
        for c in exe_paths:
            exe = c.split('\\')
            name = exe[1].split('.')[0]
            # command['windows'][name] = "{:}\{:}.exe".format(cygwin_path, c)
            cls.command['windows'][name] = c

    @classmethod
    def terminal_type(cls):
        """
        returns  darwin, cygwin, cmd, or linux
        """
        what = platform.system().lower()

        kind = 'UNDEFINED_TERMINAL_TYPE'
        if 'linux' in what:
            kind = 'linux'
        elif 'darwin' in what:
            kind = 'darwin'
        elif 'cygwin' in what:
            kind = 'cygwin'
        elif 'windows' in what:
            kind = 'windows'

        return kind

    @classmethod
    def which(cls, command):
        """
        returns the path of the command with which
        :param command: teh command
        :return: the path
        """
        t = cls.ttype()
        if 'windows' in t and cls.command_exists(name):
            return cls.command['windows'][name]
        elif 'linux' in t:
            cmd = ["which", command]
            result = subprocess.check_output(cmd).rstrip()
            if len(result) == 0:
                return None
            else:
                return result

    @classmethod
    def command_exists(cls, name):
        """
        returns True if the command exists
        :param name: 
        :return: 
        """
        t = cls.ttype()
        if 'windows' in t:
            # only for windows
            cls.find_cygwin_executables()
            return name in cls.command['windows']
        elif 'linux' in t:
            r = which(name)
            return r

    @classmethod
    def list_commands(cls):
        """
        find all cygwin commands.
        :return: 
        """
        t = cls.ttype()
        if 'windows' in t:
            # only for windows
            cls.find_cygwin_executables()
            print('\n'.join(cls.command['windows']))
        else:
            print("ERROR: this command is not supported for this OS")

    @classmethod
    def operating_system(cls):
        """
        the name of the os
        :return: the name of the os
        """
        return platform.system().lower()

    @classmethod
    def execute(cls, cmd, arguments="", shell=False, cwd=None, traceflag=True, witherror=True):
        """Run Shell command

        :param witherror: if set to fasle the error will not be printed
        :param traceflag: if set to true the trace is printed in case of an error
        :param cwd: the current working directory in whcih the command is supposed to be executed.
        :param shell: if set to true the subprocess is called as part of a shell
        :param cmd: command to run
        :param arguments: we dont know yet
        :return:
        """
        # print "--------------"
        result = None
        terminal = cls.terminal_type()
        # print cls.command
        os_command = [cmd]
        if terminal in ['linux', 'windows']:
            os_command = [cmd]
        elif 'cygwin' in terminal:
            if not cls.command_exists(cmd):
                print("ERROR: the command could not be found", cmd)
                return
            else:
                os_command = [cls.command[cls.operating_system()][cmd]]

        if isinstance(arguments, list):
            os_command = os_command + arguments
        elif isinstance(arguments, tuple):
            os_command = os_command + list(arguments)
        elif isinstance(arguments, str):
            os_command = os_command + arguments.split()
        else:
            print("ERROR: Wrong parameter type", type(arguments))

        if cwd is None:
            cwd = os.getcwd()
        try:
            if shell:
                result = subprocess.check_output(
                    os_command,
                    stderr=subprocess.STDOUT,
                    shell=True,
                    cwd=cwd)
            else:
                result = subprocess.check_output(
                    os_command,
                    # shell=True,
                    stderr=subprocess.STDOUT,
                    cwd=cwd)
        except:
            if witherror:
                Console.error("problem executing subprocess", traceflag=traceflag)
        if result is not None:
            result = result.strip().decode()
        return result

    @classmethod
    def mkdir(cls, newdir):
        """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
        """
        """http://code.activestate.com/recipes/82465-a-friendly-mkdir/"""

        newdir = path_expand(newdir)
        try:
            os.makedirs(newdir)
        except OSError as e:

            # EEXIST (errno 17) occurs under two conditions when the path exists:
            # - it is a file
            # - it is a directory
            #
            # if it is a file, this is a valid error, otherwise, all
            # is fine.
            if e.errno == errno.EEXIST and os.path.isdir(newdir):
                pass
            else:
                raise

    def unzip(cls, source_filename, dest_dir):
        """
        unzips a file into the destination directory
        :param dest_dir: the destination directory
        :return:
        """

        with zipfile.ZipFile(source_filename) as zf:
            for member in zf.infolist():
                # Path traversal defense copied from
                # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
                words = member.filename.split('/')
                path = path_expand(dest_dir)
                for word in words[:-1]:
                    drive, word = os.path.splitdrive(word)
                    head, word = os.path.split(word)
                    if word in (os.curdir, os.pardir, ''):
                        continue
                    path = os.path.join(path, word)
                zf.extract(member, path)


def main():
    """
    a test that shoudl actually be added into a nosetest
    :return: 
    """
    shell = Shell()

    print(shell.terminal_type())

    r = shell.execute('pwd')  # copy line replace
    print(r)

    # shell.list()

    # print json.dumps(shell.command, indent=4)

    # test some commands without args
    """
    for cmd in ['whoami', 'pwd']:
        r = shell._execute(cmd)
        print ("---------------------")
        print ("Command: {:}".format(cmd))
        print ("{:}".format(r))
        print ("---------------------")
    """
    r = shell.execute('ls', ["-l", "-a"])
    print(r)

    r = shell.execute('ls', "-l -a")
    print(r)

    r = shell.ls("-aux")
    print(r)

    r = shell.ls("-a", "-u", "-x")
    print(r)

    r = shell.pwd()
    print(r)


if __name__ == "__main__":
    main()
