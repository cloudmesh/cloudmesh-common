from __future__ import print_function
from pprint import pprint
import collections
import six


def key_prefix_replace(d, prefix, new_prefix=""):
    """
    replaces the list of prefix in keys of a flattened dict

    :param d: the flattened dict
    :param prefix: a list of prefixes that are replaced with a new prefix. Typically this will be ""
    :type prefix: list of str
    :param new_prefix: The new prefix. By default it is set to ""
    :return: the dict with the keys replaced as specified
    """
    items = []
    for k, v in d.items():
        new_key = k
        for p in prefix:
            new_key = new_key.replace(p, new_prefix, 1)
        items.append((new_key, v))
    return dict(items)


def flatme(d):
    o = {}
    for element in d:
        o[element] = flatten(d[element])
    return o


def flatten(d, parent_key='', sep='__'):
    """
    flattens the dict into a one dimensional dictionary

    :param d: multidimensional dict
    :param parent_key: replaces from the parent key
    :param sep: the separation character used when fattening. the default is __
    :return: the flattened dict
    """
    # http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


class FlatDict(dict):
    """
    A data structure to manage a flattened dict. It is initialized by passing the dict
    at time of initialization.
    """

    @property
    def dict(self):
        return self.__dict__

    def __init__(self, d):
        self.__dict__ = flatten(d)

    def __setitem__(self, key, item):
        """
        sets an item at a kive key

        :param key: this is the key
        :param item:  this is the item to be set
        """
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        return str(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        del self.__dict__[key]

    def keys(self):
        return list(self.__dict__.keys())

    def values(self):
        return list(self.__dict__.values())

    def __cmp__(self, dictionary):
        return cmp(self.__dict__, dictionary)

    def __contains__(self, item):
        return item in self.__dict__

    def add(self, key, value):
        self.__dict__[key] = value

    def __iter__(self):
        return iter(self.__dict__)

    def __call__(self):
        return self.__dict__

    def __getattr__(self, attr):
        return self.get(attr)


class FlatDict2(object):
    if six.PY2:
        primitive = (int, str, bool, unicode, dict, list)
    elif six.PY3:
        primitive = (int, str, bool, str, bytes, dict, list)

    @classmethod
    def is_primitive(cls, thing):
        return type(thing) in cls.primitive

    @classmethod
    def convert(cls, obj, flatten=True):
        """
            This function converts object into a Dict optionally Flattening it
            :param obj: Object to be converted
            :param flatten: boolean to specify if the dict has to be flattened
            :return dict: the dict of the object (Flattened or Un-flattened)
        """
        dict_result = cls.object_to_dict(obj)
        if flatten:
            dict_result = FlatDict(dict_result)
        return dict_result

    @classmethod
    def object_to_dict(cls, obj):
        """
            This function converts Objects into Dictionary
        """
        dict_obj = dict()
        if obj is not None:
            if type(obj) == list:
                dict_list = []
                for inst in obj:
                    dict_list.append(cls.object_to_dict(inst))
                dict_obj["list"] = dict_list

            elif not cls.is_primitive(obj):
                for key in obj.__dict__:
                    # is an object
                    if type(obj.__dict__[key]) == list:
                        dict_list = []
                        for inst in obj.__dict__[key]:
                            dict_list.append(cls.object_to_dict(inst))
                        dict_obj[key] = dict_list
                    elif not cls.is_primitive(obj.__dict__[key]):
                        temp_dict = cls.object_to_dict(obj.__dict__[key])
                        dict_obj[key] = temp_dict
                    else:
                        dict_obj[key] = obj.__dict__[key]
            elif cls.is_primitive(obj):
                return obj
        return dict_obj


'''

def main():
    d = {
        'cm_cloud': Default.cloud,
        'cm_update': '2015-06-18 22:11:48 UTC',
        'cm_user': 'gregor',
        'extra': {'created': '2015-05-21T20:37:10Z',
                  'metadata': {'base_image_ref': '398746398798372493287',
                               'description': None,
                               'image_location': 'snapshot',
                               'image_state': 'available',
                               'image_type': 'snapshot',
                               'instance_type_ephemeral_gb': '0',
                               'instance_type_flavorid': '3',
                               'instance_type_id': '1',
                               'instance_type_memory_mb': '4096',
                               'instance_type_name': 'm1.medium',
                               'instance_type_root_gb': '40',
                               'instance_type_rxtx_factor': '1.0',
                               'instance_type_swap': '0',
                               'instance_type_vcpus': '2',
                               'instance_uuid': '386473678463876387',
                               'kernel_id': None,
                               'network_allocated': 'True',
                               'owner_id': '36487264932876984723649',
                               'ramdisk_id': None,
                               'user_id': '762387463827463278649837'},
                  'minDisk': 40,
                  'minRam': 0,
                  'progress': 100,
                  'serverId': 'yiuksajhlkjahl',
                  'status': 'ACTIVE',
                  'updated': '2015-05-27T02:11:48Z'},
        'id': '39276498376478936247832687',
        'name': 'VM with Cloudmesh Configured Completely'
    }

    vm = {
        'extra': {'access_ip': '',
                  'availability_zone': 'nova',
                  'config_drive': '',
                  'created': '2015-06-19T00:06:58Z',
                  'disk_config': 'MANUAL',
                  'flavorId': '1',
                  'hostId': '',
                  'imageId': 'abcd',
                  'key': None,
                  'metadata': {},
                  'password': '********',
                  'tenantId': '1234',
                  'updated': '2015-06-19T00:06:58Z',
                  'uri': 'http://i5r.idp.iu.futuregrid.org/v2/1234/servers/abcd'},
        'id': '67f6bsf67a6b',
        'image': None,
        'name': 'gregor-cm_test',
        'private_ips': [],
        'public_ips': [],
        'size': None,
        'state': 3
    }

    pprint(d)
    pprint(flatten(d))

    f = FlatDict(d)
    pprint(f.dict)
    pprint(f.__dict__)
    print(f['cm_user'])
    print(f['extra__created'])

    print(f.cm_user)
    print(f.extra__created)

    f.cm_user = 'GREGOR'
    print(f.cm_user)

    # pprint(OpenStack_libcloud.flatten_image(d))

    # pprint(flatten(vm))

    # pprint(OpenStack_libcloud.flatten_vm(vm))


if __name__ == "__main__":
    main()

'''
