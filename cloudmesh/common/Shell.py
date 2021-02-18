"""
A convenient method to execute shell commands and return their output. Note:
that this method requires that the command be completely execute before the
output is returned. FOr many activities in cloudmesh this is sufficient.

"""

import errno
import glob
import os
import platform as os_platform
import shlex
import shutil
import subprocess
import sys
import zipfile
from distutils.spawn import find_executable
from pathlib import Path
from pipes import quote
from sys import platform
import textwrap

import psutil
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.util import path_expand, readfile


# from functools import wraps
# def timer(func):
#    @wraps(func)
#    def wrapper(*args,**kwargs):
#        print(f"{func.__name__!r} begins")
#        start_time = time.time()
#        result = func(*args,**kwargs)
#        print(f"{func.__name__!r} ends in {time.time()-start_time}  secs")
#        return result
#    return wrapper

# def NotImplementedInWindows(f):
#    def new_f(*args):
#        if sys.platform == "win32":
#            Console.error("The method {f.__name__} is not implemented in Windows,"
#                        " please implement, and/or submit an issue.")
#            sys.exit()
#        f(args)
#    return new_f

def NotImplementedInWindows():
    if sys.platform == "win32":
        Console.error(f"The method {__name__} is not implemented in Windows,"
                      " please implement, and/or submit an issue.")
        sys.exit()


class Brew(object):

    @classmethod
    def install(cls, name):

        r = Shell.brew("install", name)
        print(r)

        if "already satisfied: " + name in r:
            print(name, "... already installed")
            Console.ok(r)
        elif "Successfully installed esptool":
            print(name, "... installed")
            Console.ok(r)
        else:
            print(name, "... error")
            Console.error(r)

    @classmethod
    def version(cls, name):
        r = Shell.brew("ls", "--version", "name")
        print(r)


class Pip(object):
    @classmethod
    def install(cls, name):
        r = Shell.pip("install", "esptool")
        if "already satisfied: esptool" in r:
            print(name, "... already installed")
            Console.ok(r)
        elif "Successfully installed esptool":
            print(name, "... installed")
            Console.ok(r)
        else:
            print(name, "... error")
            Console.error(r)


class SubprocessError(Exception):
    """
    Manages the formatting of the error and stdout.
    This command should not be directly called. Instead use Shell
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
    Executes a command. This class should not be directly used, but
    instead you should use Shell.
    """

    def __init__(self, cmd, cwd=None, stderr=subprocess.PIPE,
                 stdout=subprocess.PIPE, env=None):
        """
        execute the given command
        :param cmd: the command
        :param cwd: the directory in which to execute the command
        :param stderr: the pipe for stderror
        :param stdout: the pipe for the stdoutput
        :param env:
        """
        Console.debug_msg('Running cmd: {}'.format(' '.join(map(quote, cmd))))

        proc = subprocess.Popen(cmd, stderr=stderr, stdout=stdout, cwd=cwd,
                                env=env)
        stdout, stderr = proc.communicate()

        self.returncode = proc.returncode
        self.stderr = stderr
        self.stdout = stdout

        if self.returncode != 0:
            raise SubprocessError(cmd, self.returncode, self.stderr,
                                  self.stdout)


class Shell(object):
    """
    The shell class allowing us to conveniently access many operating system commands.
    TODO: This works well on Linux and OSX, but has not been tested much on Windows
    """

    # TODO: we have not supported cygwin for a while
    # cygwin_path = 'bin'  # i copied fom C:\cygwin\bin

    command = {
        'windows': {},
        'linux': {},
        'darwin': {}
    }

    # TODO
    #
    # how do we now define dynamically functions based on a list that we want to support
    #
    # what we want is where args are multiple unlimited parameters to the function
    #
    # def f(args...):
    #     name = get the name from f
    #     a = list of args...
    #
    #    cls.execute(cmd, arguments=a, capture=True, verbose=False)
    #
    # commands = ['ps', 'ls', ..... ]
    # for c in commands:
    #    generate this command and add to this class dynamically
    #
    # or do something more simple
    #
    # ls = cls.execute('cmd', args...)

    @staticmethod
    def run_timed(label, command, encoding=None, service=None):
        """
        runs teh command and uses the StopWatch to time it
        :param label: name of the StopWatch
        :param command: the command to be executed
        :param encoding: the encoding
        :param service: a prefix to the stopwatch label
        :return:
        """
        _label = str(label)
        print(_label, command)
        StopWatch.start(f"{service} {_label}")
        result = Shell.run(command, encoding)
        StopWatch.stop(f"{service} {_label}")
        return str(result)

    @staticmethod
    def run(command, exit="; exit 0", encoding='utf-8'):
        """
        executes the command and returns the output as string
        :param command:
        :param encoding:
        :return:
        """

        if sys.platform == "win32":
            command = f"{command}"
        else:
            command = f"{command} {exit}"

        r = subprocess.check_output(command,
                                    stderr=subprocess.STDOUT,
                                    shell=True)
        if encoding is None or encoding == 'utf-8':
            return str(r, 'utf-8')
        else:
            return r

    @staticmethod
    def run2(command, encoding='utf-8'):
        """
        executes the command and returns the output as string. This command also
        allows execution of 32 bit commands.

        :param command: the program or command to be executed
        :param encoding: encoding of the output
        :return:
        """
        if platform.lower() == 'win32':
            import ctypes

            class disable_file_system_redirection:
                _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

                def __enter__(self):
                    self.old_value = ctypes.c_long()
                    self.success = self._disable(ctypes.byref(self.old_value))

                def __exit__(self, type, value, traceback):
                    if self.success:
                        self._revert(self.old_value)

            with disable_file_system_redirection():
                command = f"{command}"
                r = subprocess.check_output(command,
                                            stderr=subprocess.STDOUT,
                                            shell=True)
                if encoding is None or encoding == 'utf-8':
                    return str(r, 'utf-8')
                else:
                    return r
        elif platform.lower() == 'linux' or platform.lower() == 'darwin':
            command = f"{command}"
            r = subprocess.check_output(command,
                                        stderr=subprocess.STDOUT,
                                        shell=True)
            if encoding is None or encoding == 'utf-8':
                return str(r, 'utf-8')
            else:
                return r

    @classmethod
    def execute(cls,
                cmd,
                arguments="",
                shell=False,
                cwd=None,
                traceflag=True,
                witherror=True):
        """Run Shell command

        :param witherror: if set to False the error will not be printed
        :param traceflag: if set to true the trace is printed in case of an error
        :param cwd: the current working directory in which the command is
        supposed to be executed.
        :param shell: if set to true the subprocess is called as part of a shell
        :param cmd: command to run
        :param arguments: we do not know yet
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
        # noinspection PyPep8
        try:
            if shell:
                if platform.lower() == 'win32':
                    import ctypes

                    class disable_file_system_redirection:
                        _disable = ctypes.windll.kernel32.Wow64DisableWow64FsRedirection
                        _revert = ctypes.windll.kernel32.Wow64RevertWow64FsRedirection

                        def __enter__(self):
                            self.old_value = ctypes.c_long()
                            self.success = self._disable(
                                ctypes.byref(self.old_value))

                        def __exit__(self, type, value, traceback):
                            if self.success:
                                self._revert(self.old_value)

                    if len(os_command) == 1:
                        os_command = os_command[0].split(' ')
                    with disable_file_system_redirection():
                        result = subprocess.check_output(os_command,
                                                         stderr=subprocess.STDOUT,
                                                         shell=True,
                                                         cwd=cwd)
                else:
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
                Console.error("problem executing subprocess",
                              traceflag=traceflag)
        if result is not None:
            result = result.strip().decode()
        return result

    @staticmethod
    def oneline(script):
        """
        converts a script to one line command.
        THis is useful to run a single ssh command and pass a one line script.

        :param script:
        :return:
        """
        return " && ".join(textwrap.dedent(script).strip().splitlines())

    @staticmethod
    def is_root():
        username = subprocess.getoutput("whoami")
        return username == "root"

    @staticmethod
    def rmdir(top, verbose=False):

        p = Path(top)
        if not p.exists():
            return
        try:
            shutil.rmtree(path_expand(top))
        except OSError as e:
            print(e.strerror)
            assert False, "Directory {location} could not be deleted"

    @staticmethod
    def dot2svg(filename, engine='dot'):
        data = {
            'engine': engine,
            'file': filename.replace(".dot", "")
        }
        command = "{engine} -Tsvg {file}.dot > {file}.svg".format(**data)
        print(command)
        os.system(command)

    @staticmethod
    def browser(filename):
        data = {
            'engine': 'python -m webbrowser',
            'file': filename
        }
        if 'file:' not in filename and 'http' not in filename:
            os.system("python -m webbrowser -t file:///{file}".format(**data))
        else:
            os.system("python -m webbrowser -t {file}".format(**data))

    @staticmethod
    def terminal_title(name):
        return f'echo -n -e \"\033]0;{name}\007\"'

    @classmethod
    def terminal(cls, command='pwd', title=None):
        # title nameing not implemented
        print(platform)
        if platform == 'darwin':
            label = Shell.terminal_title(title)

            os.system(
                f"osascript -e 'tell application \"Terminal\" to do script \"{command}\"'"
            )
        elif platform == "linux":  # for ubuntu running gnome
            os.system(f"gnome-terminal -e \"bash -c \'{command}; exec $SHELL\'\"")

        elif platform == "win32":
            if Path.is_dir(Path(r"C:\Program Files\Git")):
                subprocess.Popen([r"C:\Program Files\Git\git-bash.exe",
                                  "-c", f"{command}"])
            else:
                Console.error("Git bash is not found, please make sure it "
                              "is installed.")
                raise NotImplementedError
        else:
            raise NotImplementedError

    @classmethod
    def live(cls, command, cwd=None):
        if cwd is None:
            cwd = os.getcwd()
        process = subprocess.Popen(shlex.split(command), cwd=cwd,
                                   stdout=subprocess.PIPE)
        result = b''
        while True:
            output = process.stdout.read(1)
            if output == b'' and process.poll() is not None:
                break
            if output:
                result = result + output
                sys.stdout.write(output.decode("utf-8"))
                sys.stdout.flush()
        rc = process.poll()
        data = dotdict({
            "status": rc,
            "text": output.decode("utf-8")
        })
        return data

    @classmethod
    def get_python(cls):
        """
        returns the python and pip version
        :return: python version, pip version
        """
        python_version = sys.version_info[:3]
        v_string = [str(i) for i in python_version]
        python_version_s = '.'.join(v_string)

        # pip_version = pip.__version__
        pip_version = Shell.pip("--version").split()[1]
        return python_version_s, pip_version

    @classmethod
    def check_output(cls, *args, **kwargs):
        """Thin wrapper around :func:`subprocess.check_output`
        """
        return subprocess.check_output(*args, **kwargs)

    @classmethod
    def ls(cls, match="."):
        """
        executes ls with the given arguments
        :param args:
        :return: list
        """
        d = glob.glob(match)
        return d

    @classmethod
    # @NotImplementedInWindows
    def unix_ls(cls, *args):
        """
        executes ls with the given arguments
        :param args:
        :return:
        """
        return cls.execute('ls', args)

    @staticmethod
    def ps():
        """
        using psutil to return the process information pid, name and comdline,
        cmdline may be a list

        :return: a list of dicts of process information
        """
        found = []
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline'])
            except psutil.NoSuchProcess:
                pass
            else:
                found.append(pinfo)
        if len(pinfo) == 0:
            return None
        else:
            return found

    @classmethod
    def bash(cls, *args):
        """
        executes bash with the given arguments
        :param args:
        :return:
        """
        return cls.execute('bash', args)

    @classmethod
    # @NotImplementedInWindows
    def brew(cls, *args):
        """
        executes bash with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        return cls.execute('brew', args)

    @classmethod
    # @NotImplementedInWindows
    def cat(cls, *args):
        """
        executes cat with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        # TODO: replace with file read and reading the content. We need to deal
        #       with line endings and add maybe a flag endings="unix"/"windows".
        #       check the finction readlines.
        return cls.execute('cat', args)

    @classmethod
    def git(cls, *args):
        """
        executes git with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        return cls.execute('git', args)

    # noinspection PyPep8Naming
    @classmethod
    def VBoxManage(cls, *args):
        """
        executes VboxManage with the given arguments
        :param args:
        :return:
        """

        if platform == "darwin":
            command = "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
        else:
            command = 'VBoxManage'
        return cls.execute(command, args)

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
    def cms(cls, *args):
        """
        executes cm with the given arguments
        :param args:
        :return:
        """
        return cls.execute('cms', args)

    @classmethod
    def cmsd(cls, *args):
        """
        executes cm with the given arguments
        :param args:
        :return:
        """
        return cls.execute('cmsd', args)

    @classmethod
    # @NotImplementedInWindows
    def head(cls, *args):
        """
        executes head with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        # TODO: reimplement with readlines
        return cls.execute('head', args)

    @classmethod
    def keystone(cls, *args):
        """
        executes keystone with the given arguments
        :param args:
        :return:
        """
        return cls.execute('keystone', args)

    @staticmethod
    def kill_pid(pid):

        if sys.platform == 'win32':
            try:
                result = Shell.run(f"taskkill /IM {pid} /F")
            except Exception as e:
                result = str(e)
        else:
            try:
                result = Shell.kill("-9", pid)
            except subprocess.CalledProcessError:
                result = 'server is already down...'
        return result

    @classmethod
    # @NotImplementedInWindows
    def kill(cls, *args):
        """
        executes kill with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        # TODO: use tasklisk, compare to linux
        return cls.execute('kill', args)

    @classmethod
    def mount(cls, *args):
        """
        mounts a given mountpoint to a file
        :param args:
        :return:
        """
        return cls.execute('mount', args)

    @classmethod
    def umount(cls, *args):
        """
        umounts a given mountpoint to a file
        :param args:
        :return:
        """
        return cls.execute('umount', args)

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
        option = '-n' if platform == 'windows' else '-c'
        return cls.execute('ping',
                           "{option} {count} {host}".format(option=option,
                                                            count=count,
                                                            host=host))

    @classmethod
    def pwd(cls, *args):
        """
        executes pwd with the given arguments
        :param args:
        :return:
        """
        return os.getcwd()

    @classmethod
    def rackdiag(cls, *args):
        """
        executes rackdiag with the given arguments
        :param args:
        :return:
        """
        return cls.execute('rackdiag', args)

    @classmethod
    # @NotImplementedInWindows
    def rm(cls, location):
        """
        executes rm tree with the given arguments
        :param args:
        :return:
        """
        shutil.rmtree(path_expand(location))

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
    # @NotImplementedInWindows
    def sort(cls, *args):
        """
        executes sort with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        # TODO: https://superuser.com/questions/1316317/is-there-a-windows-equivalent-to-the-unix-uniq
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
    # @NotImplementedInWindows
    def sudo(cls, *args):
        """
        executes sudo with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        # TODO: https://stackoverflow.com/questions/9652720/how-to-run-sudo-command-in-windows
        return cls.execute('sudo', args)

    @classmethod
    # @NotImplementedInWindows
    def tail(cls, *args):
        """
        executes tail with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        # TODO: implement with realines on a file.
        return cls.execute('tail', args)

    @classmethod
    def vagrant(cls, *args):
        """
        executes vagrant with the given arguments
        :param args:
        :return:
        """
        return cls.execute('vagrant', args, shell=True)

    @classmethod
    def pandoc(cls, *args):
        """
        executes vagrant with the given arguments
        :param args:
        :return:
        """
        return cls.execute('pandoc', args)

    @classmethod
    def mongod(cls, *args):
        """
        executes mongod with the given arguments
        :param args:
        :return:
        """
        return cls.execute('mongod', args)

    @classmethod
    # @NotImplementedInWindows
    def dialog(cls, *args):
        """
        executes dialof with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
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
    # @NotImplementedInWindows
    def fgrep(cls, *args):
        """
        executes fgrep with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        # TODO: see cm_grep
        return cls.execute('fgrep', args)

    @classmethod
    # @NotImplementedInWindows
    def grep(cls, *args):
        """
        executes grep with the given arguments
        :param args:
        :return:
        """
        NotImplementedInWindows()
        return cls.execute('grep', args)

    @classmethod
    def cm_grep(cls, lines, what):
        """
        returns all lines that contain what
        :param lines:
        :param what:
        :return:
        """
        result = []
        for line in lines:
            if what in line:
                result.append(line)
        return result

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

    @classmethod
    def find_lines_from(cls, lines, what):
        """
        returns all lines that come after a particular line
        :param lines:
        :param what:
        :return:
        """
        result = []
        found = False
        for line in lines:
            found = found or what in line
            if found:
                result = result + [line]
        return result

    @classmethod
    def find_lines_between(cls, lines, what_from, what_to):
        """
        returns all lines that come between the markers
        :param lines:
        :param what:
        :return:
        """
        select = Shell.find_lines_from(lines, what_from)
        select = Shell.find_lines_to(select, what_to)
        return select

    @classmethod
    def find_lines_to(cls, lines, what):
        """
        returns all lines that come before a particular line
        :param lines:
        :param what:
        :return:
        """
        result = []
        found = True
        for line in lines:
            if what in line:
                return result
            else:
                result = result + [line]
        return result

    @classmethod
    def terminal_type(cls):
        """
        returns  darwin, cygwin, cmd, or linux
        """
        what = sys.platform

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
        return find_executable(command)

    @classmethod
    def command_exists(cls, name):
        """
        returns True if the command exists
        :param name:
        :return:
        """
        return cls.which(name) is not None

    @classmethod
    def operating_system(cls):
        """
        the name of the os
        :return: the name of the os
        """
        return platform

    @staticmethod
    def get_pid(name, service="psutil"):
        pid = None
        for proc in psutil.process_iter():
            if name in proc.name():
                pid = proc.pid
        return pid

    @staticmethod
    def cms(command, encoding='utf-8'):
        return Shell.run("cms " + command, encoding=encoding)

    @classmethod
    def check_python(cls):
        """
        checks if the python version is supported
        :return: True if it is supported
        """
        python_version = sys.version_info[:3]

        v_string = [str(i) for i in python_version]

        python_version_s = '.'.join(v_string)

        if python_version[0] == 2:

            print(
                "You are running an unsupported version of python: {:}".format(
                    python_version_s))

            # python_version_s = '.'.join(v_string)
            # if (python_version[0] == 2) and (python_version[1] >= 7) and (python_version[2] >= 9):

            #    print("You are running an unsupported version of python: {:}".format(python_version_s))
            # else:
            #    print("WARNING: You are running an unsupported version of python: {:}".format(python_version_s))
            #    print("         We recommend you update your python")

        elif python_version[0] == 3:

            if (python_version[0] == 3) and (python_version[1] >= 7) and (python_version[2] >= 0):

                print(
                    "You are running a supported version of python: {:}".format(
                        python_version_s))
            else:
                print(
                    "WARNING: You are running an unsupported version of python: {:}".format(
                        python_version_s))
                print("         We recommend you update your python")

        # pip_version = pip.__version__
        python_version, pip_version = cls.get_python()

        if int(pip_version.split(".")[0]) >= 19:
            print("You are running a supported version of pip: " + str(
                pip_version))
        else:
            print("WARNING: You are running an old version of pip: " + str(
                pip_version))
            print("         We recommend you update your pip  with \n")
            print("             pip install -U pip\n")

    @classmethod
    def mkdir(cls, directory):
        """
        creates a directory with all its parents in ots name
        :param directory: the path of the directory
        :return:
        """
        directory = path_expand(directory)
        try:
            os.makedirs(directory)
        except OSError as e:

            # EEXIST (errno 17) occurs under two conditions when the path exists:
            # - it is a file
            # - it is a directory
            #
            # if it is a file, this is a valid error, otherwise, all
            # is fine.
            if e.errno == errno.EEXIST and os.path.isdir(directory):
                pass
            else:
                raise

    def unzip(cls, source_filename, dest_dir):
        """
        unzips a file into the destination directory
        :param source_filename: the source
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

    @staticmethod
    def edit(filename):
        if platform == 'darwin':
            os.system("emacs " + filename)
        elif platform == "windows":
            os.system("notepad " + filename)
        else:
            raise NotImplementedError("Editor not configured for OS")

    @classmethod
    # @NotImplementedInWindows
    def lsb_release(cls):
        """
        executes lsb_release command
        :param args:
        :return:
        """
        NotImplementedInWindows()
        return cls.execute('lsb_release', ['-a'])

    @classmethod
    def distribution(cls):
        """
        executes lsb_release command
        :param args:
        :return:

        TODO: needs testing
        """

        machine = platform.lower()

        result = {"platform": machine,
                  "distribution": None}

        if machine == "linux":
            try:
                release = readfile("/etc/os-release")
                for line in release.splitlines():
                    attribute, value = line.split("=", 1)
                    result[attribute] = value
                if "Debian" in result["NAME"]:
                    result["distribution"] = "debian"
                elif "Ubuntu" in result["NAME"]:
                    result["distribution"] = "ubuntu"

            except:
                try:
                    r = cls.lsb_release()
                    for line in r.split():
                        if ":" in line:
                            attribute, value = line.split(":", 1)
                            attribute = attribute.strip().replace(" ",
                                                                  "_").lower()
                            value = value.strip()
                            result[attribute] = value
                    result["distribution"] = result["description"].split(" ")[
                        0].lower()
                except:
                    Console.error(
                        f"lsb_release not found for the platform {machine}")
                    raise NotImplementedError
        elif machine == 'darwin':
            result["distribution"] = "macos"
            result["version"] = os_platform.mac_ver()[0]
        elif machine == 'win32':
            result["distribution"] = "windows"
            result["version"] = os_platform.win_ver()[0]
        else:
            Console.error(f"not implemented for the platform {machine}")
            raise NotImplementedError

        return result


def main():
    """
    a test that should actually be added into a pytest
    :return:
    """

    print(Shell.terminal_type())

    r = Shell.execute('pwd')  # copy line replace
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
    r = Shell.execute('ls', ["-l", "-a"])
    print(r)

    r = Shell.execute('ls', "-l -a")
    print(r)

    if sys.platform != "win32":
        r = Shell.unix_ls("-aux")
        print(r)

        r = Shell.unix_ls("-a", "-u", "-x")
        print(r)

    r = Shell.ls("./*.py")
    print(r)

    r = Shell.ls("*/*.py")
    print(r)

    r = Shell.pwd()
    print(r)


if __name__ == "__main__":
    main()
