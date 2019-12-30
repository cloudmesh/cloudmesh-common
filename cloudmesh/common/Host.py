import os
import subprocess
from multiprocessing import Pool
from sys import platform

from cloudmesh.common.parameter import Parameter
from cloudmesh.common.util import path_expand


class Host(object):

    @staticmethod
    def _ssh(args):
        """
        check a vm

        :param args: dict of {key, username, host, command}
        :return: a dict representing the result, if returncode=0 ping is
                 successfully
        """
        key = args['key']
        host = args['host']
        username = args['username']
        command = args['command']

        location = f"{username}@{host}"
        command = ['ssh',
                   "-o", "StrictHostKeyChecking=no",
                   "-o", "UserKnownHostsFile=/dev/null",
                   '-i', key, location, command]
        result = subprocess.run(command, capture_output=True)
        result.stdout = result.stdout.decode("utf-8")
        result.success = result.returncode == 0
        return result

    @staticmethod
    def ssh(hosts=None,
            command=None,
            username=None,
            key="~/.ssh/id_rsa.pub",
            processors=3):
        #
        # BUG: this code has a bug and does not deal with different
        #  usernames on the host to be checked.
        #
        """

        :param command: the command to be executed
        :param hosts: a list of hosts to be checked
        :param username: the usernames for the hosts
        :param key: the key for logging in
        :param processors: the number of parallel checks
        :return: list of dicts representing the ping result
        """

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

        if username is None:
            username = os.environ['USER']

        key = path_expand(key)

        # wrap ip and count into one list to be sent to Pool map
        args = [{'command': command,
                 'key': key,
                 'username': username,
                 'host': host} for host in hosts]

        with Pool(processors) as p:
            res = p.map(Host._ssh, args)
        return res

    @staticmethod
    def check(hosts=None,
              username=None,
              key="~/.ssh/id_rsa.pub",
              processors=3):
        #
        # BUG: this code has a bug and does not deal with different
        #  usernames on the host to be checked.
        #
        """

        :param hosts: a list of hosts to be checked
        :param username: the usernames for the hosts
        :param key: the key for logging in
        :param processors: the number of parallel checks
        :return: list of dicts representing the ping result
        """

        result = Host.ssh(hosts=hosts,
                          command='hostname',
                          username=username,
                          key=key,
                          processors=processors)

        return result

    # noinspection PyBroadException
    @staticmethod
    def _ping(args):
        """
            ping a vm

            :param args: dict of {ip address, count}
            :return: a dict representing the result, if returncode=0 ping is
                     successfully
            """
        ip = args['ip']
        count = str(args['count'])
        count_flag = '-n' if platform == 'windows' else '-c'
        command = ['ping', count_flag, count, ip]
        result = subprocess.run(command, capture_output=True)

        try:
            timers = result.stdout \
                .decode("utf-8") \
                .split("round-trip min/avg/max/stddev =")[1] \
                .replace('ms', '').strip() \
                .split("/")
            data = {
                "host": ip,
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "min": timers[0],
                "avg": timers[1],
                "max": timers[2],
                "stddev": timers[3]
            }
        except:
            data = {
                "host": ip,
                "success": result.returncode == 0,
                "stdout": result.stdout,
            }
        return data

    @staticmethod
    def ping(hosts=None, count=1, processors=3):
        """
        ping a list of given ip addresses

        :param hosts: a list of ip addresses
        :param count: number of pings to run per ip
        :param processors: number of processors to Pool
        :return: list of dicts representing the ping result
        """

        # first expand the ips to a list

        if type(hosts) != list:
            hosts = Parameter.expand(hosts)

            # wrap ip and count into one list to be sent to Pool map
        args = [{'ip': ip, 'count': count} for ip in hosts]

        with Pool(processors) as p:
            res = p.map(Host._ping, args)

        return res
