"""authorized key management."""
# TODO: needs pytests
import io
import itertools
import os.path

from cloudmesh.common.Shell import Subprocess
from cloudmesh.common.util import tempdir


# TODO:  use our simple subprocess wrapper ?

def get_fingerprint_from_public_key(pubkey):
    """Generate the fingerprint of a public key

    Args:
        pubkey (str): the value of the public key

    Returns:
        str: fingerprint
    """

    # TODO: why is there a tmpdir?
    with tempdir() as workdir:
        key = os.path.join(workdir, 'key.pub')
        with open(key, 'w') as fd:
            fd.write(pubkey)

        cmd = [
            'ssh-keygen',
            '-l',
            '-f', key,
        ]

        p = Subprocess(cmd)
        output = p.stdout.strip()
        bits, fingerprint, _ = output.split(' ', 2)
        return fingerprint


class AuthorizedKeys(object):
    """Class to manage authorized keys."""
    def __init__(self):
        self._order = dict()
        self._keys = dict()

    @classmethod
    def load(cls, path):
        """load the keys from a path

        Args:
            path: the filename (path) in which we find the keys

        Returns:

        """
        auth = cls()
        with open(path) as fd:
            for pubkey in map(str.strip, fd):
                # skip empty lines
                if not pubkey:
                    continue
                auth.add(pubkey)
        return auth

    def add(self, pubkey):
        """add a public key.

        Args:
            pubkey: the filename to the public key

        Returns:

        """
        f = get_fingerprint_from_public_key(pubkey)
        if f not in self._keys:
            self._order[len(self._keys)] = f
            self._keys[f] = pubkey

    def remove(self, pubkey):
        """Removes the public key
        TODO: this method is not implemented

        Args:
            pubkey: the filename of the public key

        Returns:

        """
        raise NotImplementedError()

    def __str__(self):
        sio = io.StringIO()

        for fingerprint in self._order.values():
            key = self._keys[fingerprint]
            sio.write(key)
            sio.write('\n')

        text = sio.getvalue()
        sio.close()

        return text.strip()


if __name__ == '__main__':
    import sys

    path = sys.argv[1]
    auth = AuthorizedKeys.load(path)
    print(auth)
