"""
Managing ~/.ssh/config
"""
import json
import os
from textwrap import dedent

from cloudmesh.common.console import Console
from cloudmesh.common.Shell import Shell


# noinspection PyPep8Naming
class ssh_config(object):
    """
    Managing the config in .ssh
    """
    def __init__(self, filename=None):
        if filename is not None:
            # load
            pass
        else:
            filename = "~/.ssh/config"

        self.filename = os.path.expanduser(filename)
        self.load()

    def names(self):
        """
        The names defined in ~/.ssh/config
        :return: the names
        """
        found_names = []
        with open(self.filename) as f:
            content = f.readlines()
        for line in content:
            line = line.strip()
            if " " in line:
                attribute, value = line.split(" ", 1)
                attribute = attribute.strip()
                value = value.strip()
                if attribute.lower() in ['host']:
                    found_names.append(value)
        return found_names

    # noinspection PyAttributeOutsideInit
    def load(self):
        """list the hosts defined in the ssh config file"""
        with open(self.filename) as f:
            content = f.readlines()
        content = [" ".join(x.split()).strip('\n').lstrip().split(' ', 1) for x in content]

        # removes duplicated spaces, and splits in two fields, removes leading spaces
        hosts = {}
        host = "NA"
        for line in content:
            if line[0].startswith('#') or line[0] == '':
                pass  # ignore line
            else:
                attribute = line[0]
                value = line[1]
                if attribute.lower().strip() in ['Host', 'host']:
                    host = value
                    hosts[host] = {'host': host}
                else:
                    # In case of special configuration lines, such as port
                    # forwarding,
                    # there would be no 'Host india' line.
                    if host in hosts:
                        hosts[host][attribute] = value
                        # pass
        self.hosts = hosts

    def list(self):
        """
        list the hosts in the config file
        :return:
        """
        return list(self.hosts.keys())

    def __str__(self):
        """
        The string representing the config file
        :return: the string representation
        """
        return json.dumps(self.hosts, indent=4)

    def status(self):
        """
        executes a test with the given ssh config if a login is possible.

        TODO: not yet implemented
        """
        pass

    def login(self, name):
        """
        login to the host defines in .ssh/config by name
        :param name: the name of the host as defined in the config file
        :return:
        """
        os.system("ssh {0}".format(name))

    def execute(self, name, command):
        """
        execute the command on the named host
        :param name: the name of the host in config
        :param command: the command to be executed
        :return:
        """
        if name in ["localhost"]:
            r = '\n'.join(Shell.sh("-c", command).split()[-1:])
        else:
            r = '\n'.join(Shell.ssh(name, command).split()[-1:])
        return r

    def local(self, command):
        """
        execute the command on the localhost
        :param command: the command to execute
        :return:
        """
        return self.execute("localhost", command)

    def username(self, host):
        """
        returns the username for a given host in the config file
        :param host: the hostname
        :return: the username
        """
        if host in self.hosts:
            return self.hosts[host]["User"]
        else:
            return None

    def generate(self,
                 host="india",
                 hostname="india.futuresystems.org",
                 identity="~/.ssh/id_rsa.pub",
                 user=None,
                 force=False,
                 verbose=False):
        """
        adds a host to the config file with given parameters.  #TODO: make sure this is better documented
        :param key: the key
        :param host: the host
        :param username: the username
        :param force: not used
        :param verbose: prints debug messages
        :return:
        """

        if verbose and host in self.names():
            Console.error(f"{host} already in ~/.ssh/config", traceflag=False)
            return ""
        else:
            entry = dedent("""
            Host {host}
                Hostname {hostname}
                User {user}
                IdentityFile {identity}
            """.format(**locals()))
        try:
            with open(self.filename, "a") as config_ssh:
                config_ssh.write(entry)
            config_ssh.close()
            self.load()
            if verbose:
                Console.ok("Added india to ~/.ssh/config")
        except Exception as e:
            if verbose:
                Console.error(e.message)


if __name__ == "__main__":
    from cloudmesh.common.ConfigDict import ConfigDict

    hosts = ssh_config()

    user = ConfigDict("cloudmesh.yaml")["cloudmesh.profile.user"]
    print("User:", user)

    hosts.generate(host="india", user=user)
    print(hosts.filename)

    print(hosts.list())
    print(hosts)

    import sys

    sys.exit()

    r = hosts.execute("india", "hostname")
    print(r)

    r = hosts.execute("localhost", "hostname")
    print(r)

    r = hosts.local("hostname")
    print(r)

    # hosts.login("india")
