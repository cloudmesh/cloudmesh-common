"""A convenient method to execute shell commands and return their output. Note:
that this method requires that the command be completely execute before the
output is returned. FOr many activities in cloudmesh this is sufficient.

"""
import os
import platform as os_platform
import shutil
import subprocess
import sys
import textwrap
import webbrowser
import zipfile
from pathlib import Path
from sys import platform

import psutil
import requests
from cloudmesh.common.StopWatch import StopWatch
from cloudmesh.common.console import Console
from cloudmesh.common.dotdict import dotdict
from cloudmesh.common.systeminfo import get_platform
from cloudmesh.common.systeminfo import os_is_linux
from cloudmesh.common.systeminfo import os_is_mac
from cloudmesh.common.systeminfo import os_is_windows
from cloudmesh.common.util import is_gitbash
from cloudmesh.common.util import path_expand
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from tqdm import tqdm

import shlex
from shlex import quote


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

def windows_not_supported(f):
    def wrapper(*args, **kwargs):
        host = get_platform()
        if host == "windows":
            Console.error("Not supported on windows")
            return ""
        else:
            return f(*args, **kwargs)

    return wrapper


def NotImplementedInWindows():
    if sys.platform == "win32":
        Console.error(f"The method {__name__} is not implemented in Windows.")
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
        r = Shell.pip("install", name)
        if f"already satisfied: {name}" in r:
            print(name, "... already installed")
            Console.ok(r)
        elif f"Successfully installed {name}":
            print(name, "... installed")
            Console.ok(r)
        else:
            print(name, "... error")
            Console.error(r)


class SubprocessError(Exception):
    """Manages the formatting of the error and stdout.
    This command should not be directly called. Instead use Shell
    """

    def __init__(self, cmd, returncode, stderr, stdout):
        """sets the error

        Args:
            cmd: the command executed
            returncode: the return code
            stderr: the stderr
            stdout: the stdout
        """
        self.cmd = cmd
        self.returncode = returncode
        self.stderr = stderr
        self.stdout = stdout

    def __str__(self):

        def indent(lines, amount, ch=' '):
            """indent the lines by multiples of ch

            Args:
                lines
                amount
                ch

            Returns:

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
    """Executes a command. This class should not be directly used, but
    instead you should use Shell.
    """

    def __init__(self, cmd, cwd=None, stderr=subprocess.PIPE,
                 stdout=subprocess.PIPE, env=None):
        """execute the given command

        Args:
            cmd: the command
            cwd: the directory in which to execute the command
            stderr: the pipe for stderror
            stdout: the pipe for the stdoutput
            env
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
    """The shell class allowing us to conveniently access many operating system commands.
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
    def timezone(default="America/Indiana/Indianapolis"):
        # BUG we need to be able to pass the default from the cmdline
        host = get_platform()
        if host == "windows":
            return default
        else:
            # result = Shell.run("ls -l /etc/localtime").strip().split("/")
            try:
                result = Shell.run("ls -l /etc/localtime").strip().split("zoneinfo")[1][1:]
                return result
            except IndexError as e:
                return default

    @staticmethod
    @windows_not_supported
    def locale():
        try:
            result = Shell.run('locale').split('\n')[0].split('_')[1].split('.')[0].lower()
            return result
        except IndexError as e:
            Console.warning('Could not determine locale. Defaulting to "us"')
            return 'us'

    @staticmethod
    def ssh_enabled():
        if os_is_linux():
            try:
                r = Shell.run("which sshd")
            except RuntimeError as e:
                raise RuntimeError("You do not have OpenSSH installed. " 
                                    "sudo apt-get install openssh-client openssh-server "
                                    "Automatic installation will be implemented in future cloudmesh version.")
            # the reason why we do it like this is because WSL
            # does not have sshd as a status. this works fine
            r = Shell.run("service ssh status | fgrep running").strip()
            
            return len(r) > 0
        elif os_is_windows():
            # r = Shell.run("ps | grep -F ssh")
            # return "ssh" in r
            processes = psutil.process_iter(attrs=['name'])
            # Filter the processes for 'ssh'
            ssh_processes = [p.info for p in processes if 'ssh' in p.info['name']]
            return len(ssh_processes) > 0

        elif os_is_mac():
            r = Shell.run("ps -ef")
            if "sshd" in r:
                print('IT WORKS!!!!!')
            else:
                print('it doenst work :(')
            return "sshd" in r
        return False

    @staticmethod
    def run_timed(label, command, encoding=None, service=None):
        """runs the command and uses the StopWatch to time it

        Args:
            label: name of the StopWatch
            command: the command to be executed
            encoding: the encoding
            service: a prefix to the stopwatch label

        Returns:

        """
        _label = str(label)
        print(_label, command)
        StopWatch.start(f"{service} {_label}")
        result = Shell.run(command, encoding)
        StopWatch.stop(f"{service} {_label}")
        return str(result)

    @staticmethod
    def run(command, exitcode="", encoding='utf-8', replace=True, timeout=None):
        """executes the command and returns the output as string

        Args:
            command
            encoding

        Returns:

        """

        if sys.platform == "win32":
            if replace:
                c = "&"
            else:
                c = ";"
            command = f"{command}".replace(";", c)
        elif exitcode:
            command = f"{command} {exitcode}"

        try:
            if timeout is not None:
                r = subprocess.check_output(command,
                                            stderr=subprocess.STDOUT,
                                            shell=True,
                                            timeout=timeout)
            else:
                r = subprocess.check_output(command,
                                            stderr=subprocess.STDOUT,
                                            shell=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"{e.returncode} {e.output.decode()}")
        if encoding is None or encoding == 'utf-8':
            return str(r, 'utf-8')
        else:
            return r

    @staticmethod
    def run2(command, encoding='utf-8'):
        """executes the command and returns the output as string. This command also
        allows execution of 32 bit commands.

        Args:
            command: the program or command to be executed
            encoding: encoding of the output

        Returns:

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

        Args:
            witherror: if set to False the error will not be printed
            traceflag: if set to true the trace is printed in case of an
                error
            cwd: the current working directory in which the command is
            shell: if set to true the subprocess is called as part of a
                shell
            cmd: command to run
            arguments: we do not know yet
        supposed to be executed.

        Returns:

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
        except:  # noqa: E722
            if witherror:
                Console.error("problem executing subprocess",
                              traceflag=traceflag)
        if result is not None:
            result = result.strip().decode()
        return result

    @staticmethod
    def oneline(script, seperator=" && "):
        """converts a script to one line command.
        THis is useful to run a single ssh command and pass a one line script.

        Args:
            script

        Returns:

        """
        return seperator.join(textwrap.dedent(script).strip().splitlines())

    @staticmethod
    def is_choco_installed():
        """return true if chocolatey windows package manager is installed
        return false if not installed or if not windows
        """
        if not os_is_windows():
            return False
        try:
            r = Shell.run('choco --version')
            # no problem
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def install_chocolatey():
        """install chocolatey windows package manager
        windows only
        """

        import subprocess
        import pyuac

        if os_is_windows():

            try:
                r = Shell.run('choco --version')
                Console.ok("Chocolatey already installed")
                return True
            except subprocess.CalledProcessError:
                Console.msg("Installing chocolatey...")
                if not pyuac.isUserAdmin():
                    Console.error("Please run the terminal as administrator.")
                    return False
                
                # Get the full path of the current Python script
                current_script_path = os.path.abspath(__file__)

                # Get the directory containing the current script
                script_directory = os.path.dirname(current_script_path)

                # Join the script directory with "bin"
                bin_directory = os.path.join(script_directory, 'bin')
                print(f'Looking in {bin_directory} for install script...')

                # Command to install Chocolatey using the Command Prompt
                chocolatey_install_command = fr'powershell Start-Process -Wait -FilePath {bin_directory}\win-setup.bat'
                print(chocolatey_install_command)
                # Run the Chocolatey installation command using subprocess and capture output
                completed_process = subprocess.run(chocolatey_install_command,
                                                   shell=True, text=True,
                                                   stdout=subprocess.PIPE,
                                                   stderr=subprocess.PIPE)
                if 'current directory is invalid' in str(completed_process):
                    Console.error("You are currently standing in a non-existent directory.")
                    return False
                print(completed_process)
                Console.ok("Chocolatey installed")
                return True
                # try:
                    # process = subprocess.run('choco --version')
                    # Console.ok("Chocolatey installed")
                    # return True
                # except subprocess.CalledProcessError:
                    # Console.error("Chocolatey was not added to path. Close and reopen terminal and execute previous command again.")
                    # return True
                    # pass
                # except FileNotFoundError:
                    # Console.error("Chocolatey was not added to path. Close and reopen terminal and execute previous command again.")
                    # return True
                    # pass
        else:
            Console.error("chocolatey can only be installed in Windows")
            return False

    @staticmethod
    def install_choco_package(package: str):
        if not Shell.is_choco_installed():
            Console.error("Chocolatey not installed, or terminal needs to be reloaded.")
            return False

        command = f'cmd.exe /K choco install {package} -y'

        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True  # Allows working with text output
        )

        # Read and display the live output
        for line in process.stdout:
            print(line, end="")

        # Wait for the subprocess to complete
        process.wait()
        return True
    

    @staticmethod
    def install_brew():
        # from elevate import elevate

        # elevate()


        if not os_is_mac():
            Console.error("Homebrew can only be installed on mac")
            return False
        
        try:
            r = subprocess.check_output("brew --version",
                                        stderr=subprocess.STDOUT,
                                        shell=True)
            Console.ok("Homebrew already installed")
            return True
        except subprocess.CalledProcessError:
            Console.info("Installing Homebrew...")

        
        content = """#!/bin/bash    
        pw="$(osascript -e 'Tell application "System Events" to display dialog "Please enter your macOS password to install Homebrew:" default answer "" with hidden answer' -e 'text returned of result' 2>/dev/null)" && echo "$pw"
        """

        askpass = os.path.expanduser('~/pw.sh')

        if not os.path.isfile(askpass):
            writefile(askpass, content)
        os.system('chmod +x ~/pw.sh')
        
        # command = 'NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
        command = f'osascript -e \'tell application "Terminal" to do script "/bin/bash -c \\"export SUDO_ASKPASS={askpass} ; export NONINTERACTIVE=1 ; $(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\\""\''
        print(command)
        # try:
        subprocess.run(command, shell=True, check=True)
            # print("Homebrew installed successfully.")
        # except subprocess.CalledProcessError as e:
            # print(f"Error while installing Homebrew: {e}")

        while True:
            from time import sleep
            try:
                r = subprocess.check_output("brew --version",
                                            stderr=subprocess.STDOUT,
                                            shell=True)
                Console.ok("Homebrew installed")
                sleep(8)
                return True
            except subprocess.CalledProcessError:
                # print('Waiting', end=' ')
                
                sleep(2)
                continue
                # Console.error("Homebrew could not be installed.")
                # return False
        
        Shell.rm(askpass)
            

    @staticmethod
    def is_root():
        """checks if the user is root

        Returns:
            boolean: True if the user is root
        """
        username = subprocess.getoutput("whoami")
        return username == "root"

    @staticmethod
    def rmdir(top, verbose=False):
        """removes a directory

        Args:
            top (str): removes the directory tree from the top
            verbose (unused): unused

        Returns:
            void: void
        """
        p = Path(top)
        if not p.exists():
            return
        try:
            shutil.rmtree(path_expand(top))
        except Exception as e:
            print(e)
            pass
            # print(e.strerror)
            # assert False, f"Directory {top} could not be deleted"

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
    def map_filename(name):
        pwd = os.getcwd()

        _name = str(name)
        result = dotdict()

        if os_is_windows():
            if "USERNAME" in os.environ:
                result.user = os.path.basename(os.environ["USERNAME"])
            else:
                Console.error("Could not detect the home directory")
        else:
            result.user = os.path.basename(os.environ["HOME"])
        result.host = "localhost"
        result.protocol = "localhost"

        if _name.startswith("file:"):
            _name = _name.replace("file:", "")
        if _name == "":
            result.path = ""
            if result.host == "localhost":
                _name = "."


        if _name.startswith("http"):
            result.path = _name
            result.protocol = _name.split(':', 1)[0]
        elif _name.startswith("wsl:"):
            result.path = _name.replace("wsl:", "")
            # Abbreviations: replace ~ with home dir and ./ + / with pwd
            if result.path.startswith("~"):
                if os_is_linux():
                    result.path = result.path.replace("~", f"/mnt/c/home/{result.user}")
                else:
                    result.path = result.path.replace("~", f"/mnt/c/Users/{result.user}")
            elif not result.path.startswith("/"):
                if os_is_windows():
                    pwd = pwd.replace("C:", "/mnt/c").replace("\\", "/")
                result.path = pwd + "/" + result.path.replace("./", "")
            result.protocol = "cp"
            result.host = "wsl"
        elif _name.startswith("scp:"):
            # scp source destination
            # command = f"scp:username@host:hi.txt"
            try:
                result.scp, userhost, result.path = _name.split(":")
                result.user, result.host = userhost.split("@")
                result.protocol = "scp"
            except:  # noqa: E722
                Console.error(f"The format of the name is not supported: {name}")
        elif _name.startswith("rsync:"):
            try:
                result.rsync, userhost, result.path = _name.split(":")
                result.user, result.host = userhost.split("@")
                result.protocol = "rsync"
            except:  # noqa: E722
                Console.error(f"The format of the name is not supported: {name}")
        elif _name.startswith("ftp:"):
            # expecting the following format: ftp://user:password@myftpsite/myfolder/myfile.txt
            try:
                result.ftp_location, result.ftp_path = _name.split("@")
                result.ftp_prefix, result.ftp_login = result.ftp_location.split("//")
                result.username, result.password = result.ftp_login.split(":")
                result.protocol = "ftp"
            except:  # noqa: E722
                Console.error(f"The format of the name is not supported: {name}")
        elif _name.startswith("."):
            _name = "./" + _name
            result.path = Path(path_expand(_name)).resolve()
        elif _name.startswith("~"):
            result.path = path_expand(_name)
        elif _name[1] == ":":
            drive, path = _name.split(":", 1)
            if os_is_windows():
                result.path = path_expand(path)
            else:
                result.path = drive + ":" + path_expand(path)
            result.path = result.path.replace("/", "\\")
        else:
            result.path = path_expand(_name)

        return result

    @staticmethod
    def browser(filename=None):
        """
        Args:
            filename

        Returns:

        """
        if not os.path.isabs(filename) and 'http' not in filename:
            filename = Shell.map_filename(filename).path
        webbrowser.open(filename, new=2, autoraise=False)

    @staticmethod
    def fetch(filename=None, destination=None):
        _filename = Shell.map_filename(filename)

        content = None

        if _filename.path.startswith('http'):
            result = requests.get(_filename.path)
            content = result.text

        else:
            os.path.exists(_filename.path)
            content = readfile(_filename.path)

        if destination is not None:
            destination = Shell.map_filename(destination)
            writefile(destination, content)

        return content

    @staticmethod
    def terminal_title(name):
        """sets the title of the terminal

        Args:
            name (str): the title

        Returns:
            void: void
        """
        return f'echo -n -e \"\033]0;{name}\007\"'

    @classmethod
    def terminal(cls, command='pwd', title=None, kind=None):
        """starts a terminal and executes the command in that terminal

        Args:
            command (str): the command to be executed
            title (str): the title
            kind (str): for windows you can set "cmd", "powershell", or
                "gitbash"

        Returns:
            void: void
        """
        # title nameing not implemented
        print(platform)
        if platform == 'darwin':
            label = Shell.terminal_title(title)

            os.system(
                f"osascript -e 'tell application \"Terminal\" to do script \"{command}\"'"
            )
        elif platform == "linux":  # for ubuntu running gnome
            dist = os_platform.linux_distribution()[0]
            linux_apps = {'ubuntu': 'gnome-terminal', 'debian': 'lxterminal'}
            os.system(f"{linux_apps[dist]} -e \"bash -c \'{command}; exec $SHELL\'\"")

        elif platform == "win32":
            if kind is None:
                if Path.is_dir(Path(r"C:\Program Files\Git")):
                    kind = "gitbash"
            kind = kind.lower()
            if kind == "gitbash":
                p = subprocess.Popen([r"C:\Program Files\Git\git-bash.exe",
                                      "-c",
                                      f"{command}"])
                return p.pid
            elif kind == "cmd":
                Console.error(f"Command not implemented for {kind}")
            elif kind == "powershell":
                Console.error(f"Command not implemented for {kind}")
            else:
                Console.error("Git bash is not found, please make sure it "
                              "is installed. Other terminals not supported.")
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
        """returns the python and pip version

        Returns:
            python version, pip version
        """
        python_version = sys.version_info[:3]
        v_string = [str(i) for i in python_version]
        python_version_s = '.'.join(v_string)

        # pip_version = pip.__version__
        pip_version = Shell.pip("--version").split()[1]
        return python_version_s, pip_version

    @classmethod
    def check_output(cls, *args, **kwargs):
        """Thin wrapper around :func:`subprocess.check_output`"""
        return subprocess.check_output(*args, **kwargs)

    @classmethod
    def ls(cls, directory=".", match=None):
        """executes ls with the given arguments

        Args:
            args

        Returns:
            list
        """
        import re
        if match == None:
            files = os.listdir('.')
        else:
            files = [f for f in os.listdir('.') if re.match(match, f)]
        return files

    @classmethod
    def gpu_name(cls):
        name = None
        try:
            name = Shell.run("nvidia-smi --query-gpu=gpu_name --format=csv,noheader")
        except:
            pass
        return name

    @classmethod
    def gpu_name(cls):
        content = None
        try:
            name = Shell.run("nvidia-smi")
        except:
            pass
        return content

    @classmethod
    # @NotImplementedInWindows
    def unix_ls(cls, *args):
        """executes ls with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('ls', args)

    @staticmethod
    def ps(short=False, attributes=None):
        """using psutil to return the process information pid, name and comdline,
        cmdline may be a list

        Returns:
            a list of dicts of process information
        """
        found = []
        for proc in psutil.process_iter():
            try:
                if attributes is not None:
                    pinfo = proc.as_dict(attrs=attributes)
                elif short:
                    pinfo = proc.as_dict(attrs=['pid', 'name', 'cmdline', 'ppid', 'username',
                                                'status', 'create_time', 'terminal', 'cwd',
                                                'open_files'])
                else:
                    pinfo = proc.as_dict()
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
        """executes bash with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('bash', args)

    @classmethod
    # @NotImplementedInWindows
    def brew(cls, *args):
        """executes bash with the given arguments

        Args:
            *args

        Returns:

        """
        NotImplementedInWindows()
        return cls.execute('brew', args)

    @classmethod
    # @NotImplementedInWindows
    def cat(cls, *args):
        """executes cat with the given arguments

        Args:
            *args

        Returns:

        """
        if os_is_windows() and is_gitbash():
            content = readfile(args[0])
            return content
        else:
            return cls.execute('cat', args)

    @classmethod
    def git(cls, *args):
        """executes git with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('git', args)

    # noinspection PyPep8Naming
    @classmethod
    def VBoxManage(cls, *args):
        """executes VboxManage with the given arguments

        Args:
            *args

        Returns:

        """

        if platform == "darwin":
            command = "/Applications/VirtualBox.app/Contents/MacOS/VBoxManage"
        else:
            command = 'VBoxManage'
        return cls.execute(command, args)

    @classmethod
    def blockdiag(cls, *args):
        """executes blockdiag with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('blockdiag', args)

    @classmethod
    def cm(cls, *args):
        """executes cm with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('cm', args)

    @classmethod
    def cms(cls, *args):
        """executes cm with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('cms', args)

    @classmethod
    def cmsd(cls, *args):
        """executes cm with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('cmsd', args)

    @classmethod
    def head(cls, filename=None, lines=10):
        """executes head with the given arguments

        Args:
            args

        Returns:

        """
        filename = cls.map_filename(filename).path
        r = Shell.run(f'head -n {lines} {filename}')
        return r

    @classmethod
    def keystone(cls, *args):
        """executes keystone with the given arguments

        Args:
            *args

        Returns:

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
        """executes kill with the given arguments

        Args:
            *args

        Returns:

        """
        NotImplementedInWindows()
        # TODO: use tasklisk, compare to linux
        return cls.execute('kill', args)

    @classmethod
    def download(cls, source, destination, force=False, provider=None, chunk_size=128):
        """Given a source url and a destination filename, download the file at the source url
        to the destination.

        If provider is None, the request lib is used
        If provider is 'system', wget, curl, and requests lib are attempted in that order
        """
        destination = path_expand(destination)

        if os.path.exists(destination) and not force:
            return destination

        if provider == 'system':
            # First try wget
            wget_return = os.system(f'wget -O {destination} {source}')
            if wget_return == 0:
                Console.info('Used wget')
                return destination
            # Then curl
            curl_return = os.system(f'curl -L -o {destination} {source}')
            if curl_return == 0:
                Console.info('Used curl')
                return destination
        # Default is requests lib. If provider is None, or if provider == 'system'
        # but wget and curl fail, default here
        r = requests.get(source, stream=True, allow_redirects=True)
        total_size = int(r.headers.get('content-length'))

        with open(destination, 'wb') as fd:
            with tqdm(total=total_size, unit="B",
                      unit_scale=True, desc=destination, initial=0, ascii=True) as pbar:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fd.write(chunk)
                    pbar.update(len(chunk))

            return destination

    @classmethod
    def mount(cls, *args):
        """mounts a given mountpoint to a file

        Args:
            *args

        Returns:

        """
        return cls.execute('mount', args)

    @classmethod
    def umount(cls, *args):
        """umounts a given mountpoint to a file

        Args:
            *args

        Returns:

        """
        return cls.execute('umount', args)

    @classmethod
    def nova(cls, *args):
        """executes nova with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('nova', args)

    @classmethod
    def ping(cls, host=None, count=1):
        """execute ping

        Args:
            host: the host to ping
            count: the number of pings

        Returns:

        """
        r = None
        option = '-n' if os_is_windows() else '-c'
        parameters = "{option} {count} {host}".format(option=option,
                                                      count=count,
                                                      host=host)
        r = Shell.run(f'ping {parameters}')
        if r is None:
            Console.error("ping is not installed")
        return r

    @classmethod
    def pwd(cls, *args):
        """executes pwd with the given arguments

        Args:
            *args

        Returns:

        """
        return os.getcwd()

    @classmethod
    def rackdiag(cls, *args):
        """executes rackdiag with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('rackdiag', args)

    def count_files(directory, recursive=False):
        count = 0
        if recursive:
            for root, dirs, files in os.walk(directory):
                count += len(files)
        else:
            try:
                files = os.listdir(directory)
                count = len(files)
            except FileNotFoundError:
                Console.error(f"The directory '{directory}' does not exist.")

        return count

    @classmethod
    def rm(cls, location):
        """executes rm with the given arguments

        Args:
            args

        Returns:

        """
        try:
            location = cls.map_filename(location).path
            os.remove(location)
        except:
            pass
    @classmethod
    def rsync(cls, *args):
        """executes rsync with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('rsync', args)

    @classmethod
    def scp(cls, *args):
        """executes scp with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('scp', args)

    @classmethod
    # @NotImplementedInWindows
    def sort(cls, *args):
        """executes sort with the given arguments

        Args:
            *args

        Returns:

        """
        NotImplementedInWindows()
        # TODO: https://superuser.com/questions/1316317/is-there-a-windows-equivalent-to-the-unix-uniq
        return cls.execute('sort', args)

    @classmethod
    def sh(cls, *args):
        """executes sh with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('sh', args)

    @classmethod
    def ssh(cls, *args):
        """executes ssh with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('ssh', args)

    @classmethod
    # @NotImplementedInWindows
    def sudo(cls, *args):
        """executes sudo with the given arguments

        Args:
            *args

        Returns:

        """
        NotImplementedInWindows()
        # TODO: https://stackoverflow.com/questions/9652720/how-to-run-sudo-command-in-windows
        return cls.execute('sudo', args)

    @classmethod
    def tail(cls, filename=None, lines=10):
        """executes tail with the given arguments

        Args:
            args

        Returns:

        """
        filename = cls.map_filename(filename).path
        r = Shell.run(f'tail -n {lines} {filename}')
        return r

    @classmethod
    def vagrant(cls, *args):
        """executes vagrant with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('vagrant', args, shell=True)

    @classmethod
    def pandoc(cls, *args):
        """executes vagrant with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('pandoc', args)

    @classmethod
    def mongod(cls, *args):
        """executes mongod with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('mongod', args)

    @classmethod
    # @NotImplementedInWindows
    def dialog(cls, *args):
        """executes dialof with the given arguments

        Args:
            *args

        Returns:

        """
        NotImplementedInWindows()
        return cls.execute('dialog', args)

    @classmethod
    def pip(cls, *args):
        """executes pip with the given arguments

        Args:
            *args

        Returns:

        """
        return cls.execute('pip', args)

    @classmethod
    def fgrep(cls, string=None, file=None):
        if not os_is_windows():
            r = Shell.run(f'fgrep {string} {file}')
        else:
            r = Shell.run(f'grep -F {string} {file}')
        return r

    @classmethod
    def grep(cls, string=None, file=None):
        r = Shell.run(f'grep {string} {file}')
        return r

    @classmethod
    def cm_grep(cls, lines, what):
        """returns all lines that contain what

        Args:
            lines
            what

        Returns:

        """
        if type(lines) == str:
            _lines = lines.splitlines()
        else:
            _lines = lines
        result = []
        for line in _lines:
            if what in line:
                result.append(line)
        return result

    @classmethod
    def remove_line_with(cls, lines, what):
        """returns all lines that do not contain what

        Args:
            lines
            what

        Returns:

        """
        if type(lines) == str:
            _lines = lines.splitlines()
        else:
            _lines = lines
        result = []
        for line in _lines:
            if what not in line:
                result = result + [line]
        return result

    @classmethod
    def find_lines_with(cls, lines, what):
        """returns all lines that contain what

        Args:
            lines
            what

        Returns:

        """
        if type(lines) == str:
            _lines = lines.splitlines()
        else:
            _lines = lines
        result = []
        for line in _lines:
            if what in line:
                result = result + [line]
        return result

    @classmethod
    def find_lines_from(cls, lines, what):
        """returns all lines that come after a particular line

        Args:
            lines
            what

        Returns:

        """
        if type(lines) == str:
            _lines = lines.splitlines()
        else:
            _lines = lines
        result = []
        found = False
        for line in _lines:
            found = found or what in line
            if found:
                result = result + [line]
        return result

    @classmethod
    def find_lines_between(cls, lines, what_from, what_to):
        """returns all lines that come between the markers

        Args:
            lines
            what

        Returns:

        """
        select = Shell.find_lines_from(lines, what_from)
        select = Shell.find_lines_to(select, what_to)
        return select

    @classmethod
    def find_lines_to(cls, lines, what):
        """returns all lines that come before a particular line

        Args:
            lines
            what

        Returns:

        """
        if type(lines) == str:
            _lines = lines.splitlines()
        else:
            _lines = lines
        result = []
        found = True
        for line in _lines:
            if what in line:
                return result
            else:
                result = result + [line]
        return result

    @classmethod
    def terminal_type(cls):
        """returns  darwin, cygwin, cmd, or linux"""
        what = sys.platform

        kind = 'UNDEFINED_TERMINAL_TYPE'
        if 'linux' in what:
            kind = 'linux'
        elif 'darwin' in what:
            kind = 'darwin'
        elif 'cygwin' in what:
            kind = 'cygwin'
        elif what in ['windows', 'win32']:
            kind = 'windows'

        return kind

    @classmethod
    def which(cls, command):
        """returns the path of the command with which

        Args:
            command: teh command

        Returns:
            the path
        """
        if os_is_windows():
            return Shell.run(f"where {command}")
        else:
            return shutil.which(command)

    @classmethod
    def command_exists(cls, name):
        """returns True if the command exists

        Args:
            name

        Returns:

        """
        return cls.which(name) is not None

    @classmethod
    def operating_system(cls):
        """the name of the os

        Returns:
            the name of the os
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
        """checks if the python version is supported

        Returns:
            True if it is supported
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
    def copy_source(cls, source, destination):
        """copys a file or a directory to the destination

        Args:
            destination (str): destination directory

        Returns:
            None: None
        """
        try:
            if os.path.isfile(source):  # If the source is a file
                shutil.copy2(source, destination)
            elif os.path.isdir(source):  # If the source is a directory
                shutil.copytree(source, os.path.join(destination, os.path.basename(source)))
            else:
                Console.error(f"'{source}' is neither a file nor a directory.")
        except Exception as e:
            Console.error(f"An error occurred: {e}")

    @classmethod
    def copy(cls, source, destination, expand=False):
        if expand:
            s = path_expand(source)
            d = path_expand(destination)
        else:
            s = source
            d = destination
        shutil.copy2(s, d)

    @classmethod
    def copy_file(cls, source, destination, verbose=False):

        try:
            s = Shell.map_filename(source)
            d = Shell.map_filename(destination)
            if verbose:
                print("copy")
                print("    source     :", s.path)
                print("    destination:", d.path)

            if s.protocol in ['http', 'https']:
                command = f'curl {s.path} -o {d.path}'
                Shell.run(command)
            elif s.protocol == 'scp':
                Shell.run(f'scp {s.user}@{s.host}:{s.path} {d.path}')
            elif s.protocol == 'ftp':
                command = fr"curl -u {s.username}:{s.password} ftp://{s.ftp_path} -o {d.path}"
                print(command)
                Shell.run(command)
            elif d.protocol == 'ftp':
                command = fr"curl -T {s.path} ftp://{d.ftp_path} --user {d.username}:{d.password}"
                print(command)
                Shell.run(command)
            else:
                dest_dir = os.path.dirname(d.path)
                Shell.mkdir(dest_dir)
                shutil.copy2(s.path, d.path)
        except Exception as e:
            Console.error(e, traceflag=True)

    @classmethod
    def mkdir(cls, directory):
        """creates a directory with all its parents in ots name

        Args:
            directory: the path of the directory

        Returns:

        """
        d = cls.map_filename(directory).path
        try:
            Path.mkdir(d, parents=True, exist_ok=True)
            return True
        except Exception as e:
            try:
                if not os.path.exists(d):
                    os.makedirs(d)
                    return True
            except Exception as e:
                Console.error(e, traceflag=True)
        return False


    def unzip(cls, source_filename, dest_dir):
        """unzips a file into the destination directory

        Args:
            source_filename: the source
            dest_dir: the destination directory

        Returns:

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
        """opens an editing program to edit specified filename

        Args:
            filename: file to edit

        Returns:
            nothing
        """
        if os_is_mac():
            # try to see what programs are available
            def try_program(program):
                r = Shell.run(f'''mdfind "kMDItemKind == 'Application'"''')
                if program not in r.lower():
                    return False
                return True

            def run_edit_program(program, file):
                cmd = f'''
                osascript <<EOF
                tell application "Terminal"
                    do script "{program} {file}"
                    activate
                    set frontmost to true
                end tell
                EOF
                '''
                try:
                    subprocess.check_output(cmd, shell=True)
                except:  # noqa: E722
                    pass

            if try_program('aquamacs'):
                try:
                    subprocess.check_output(f"aquamacs {filename}", shell=True)
                except:  # noqa: E722
                    pass
            elif try_program('emacs'):
                run_edit_program('emacs', filename)
            else:
                run_edit_program('nano', filename)
        elif os_is_linux():
            os.system(f'x-terminal-emulator -e "nano {filename}"')
        elif os_is_windows():
            os.system("start nano " + filename)

    @classmethod
    # @NotImplementedInWindows
    def lsb_release(cls):
        """executes lsb_release command

        Args:
            args

        Returns:

        """
        NotImplementedInWindows()
        return cls.execute('lsb_release', ['-a'])

    @classmethod
    def distribution(cls):
        """executes lsb_release command

        Args:
            args

        Returns:

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

            except:  # noqa: E722
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
                except:  # noqa: E722
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

    @staticmethod
    def open(filename=None, program=None):
        if not os.path.isabs(filename):
            filename = path_expand(filename)

        if os_is_linux() and ".svg" in filename:
            r = os.system(f"eog {filename} &")
        if os_is_linux():
            r = os.system(f"gopen {filename}")
        if os_is_mac():
            command = f'open {filename}'
            if program:
                command += f' -a "{program}"'
            r = Shell.run(command)
        if os_is_windows():
            r = Shell.run(f"start {filename}")

        return r

    @staticmethod
    def sys_user():
        if os_is_windows():
            localuser = os.environ["USERNAME"]
        else:
            try:
                localuser = os.environ['USER']
            except:
                # docker image does not have user variable. so just do whoami
                localuser = Shell.run('whoami')
        return localuser

    @staticmethod
    def user():
        return str(Shell.sys_user())

    # @staticmethod
    # def host():
    #    return str(Shell.run("hostname").strip())

    @staticmethod
    def host():
        return os_platform.node()


def main():
    """a test that should actually be added into a pytest

    Returns:

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