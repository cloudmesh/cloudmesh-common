from pprint import pprint


class DictList(dict):
    """
    A class to convert lists of dicts to dicts.

    Example:

        data = [
        {"name": "vm1", "status": "on"},
        {"name": "vm2", "status": "on"},
        {"name": "vm3", "status": "on"},
        {"name": "vm4", "status": "on"},
        ]

        d = DictList(data)
        pprint (d)

        # {'vm1': {'name': 'vm1', 'status': 'on', 'x': 0},
        #  'vm2': {'name': 'vm2', 'status': 'on', 'x': 1},
        #  'vm3': {'name': 'vm3', 'status': 'on', 'x': 2},
        #  'vm4': {'name': 'vm4', 'status': 'on', 'x': 3}}

        print (d['vm1'])
        # {'name': 'vm1', 'status': 'on', 'x': 0}
        #
        print (d.list())
        # [{'name': 'vm1', 'status': 'on', 'x': 0},
        #  {'name': 'vm2', 'status': 'on', 'x': 1},
        #  {'name': 'vm3', 'status': 'on', 'x': 2},
        #  {'name': 'vm4', 'status': 'on', 'x': 3}]


    """

    def __init__(self, entries=None, key='name', position='x'):
        """
        initializes the DotDict List

        :param entries: a list of dict
        :param key: a key that is used as name within the dict
        :param position: the name of a key that stores the order
        """

        if type(entries) == list:
            counter = 0
            for entry in entries:
                entry[position] = counter
                self[entry[key]] = entry
                counter = counter + 1
        elif type(entries) == dict:
            # noinspection PyUnusedLocal
            self = entries
        else:
            raise ValueError("type not supported")

    def list(self):
        """
        Lists the entries

        :return:
        """
        return list(self.values())


if __name__ == "__main__":
    data = [
        {"name": "vm1", "status": "on"},
        {"name": "vm2", "status": "on"},
        {"name": "vm3", "status": "on"},
        {"name": "vm4", "status": "on"},
    ]

    d = DictList(data)
    pprint(d)

    # {'vm1': {'name': 'vm1', 'status': 'on', 'x': 0},
    #  'vm2': {'name': 'vm2', 'status': 'on', 'x': 1},
    #  'vm3': {'name': 'vm3', 'status': 'on', 'x': 2},
    #  'vm4': {'name': 'vm4', 'status': 'on', 'x': 3}}

    print(d['vm1'])
    # {'name': 'vm1', 'status': 'on', 'x': 0}
    #
    print(d.list())
    # [{'name': 'vm1', 'status': 'on', 'x': 0},
    #  {'name': 'vm2', 'status': 'on', 'x': 1},
    #  {'name': 'vm3', 'status': 'on', 'x': 2},
    #  {'name': 'vm4', 'status': 'on', 'x': 3}]
