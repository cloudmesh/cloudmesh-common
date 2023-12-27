import collections
import json
import os
import re

import yaml
from cloudmesh.common.util import readfile
from cloudmesh.common.util import writefile
from cloudmesh.common.variables import Variables

"""
FlatDict can also expand variables defined in yaml files

from FlatDict

f = FlatDict(sep=".")

# filename = "config-new.yaml"
# f.loadf(filename=filename)
# print ("Load from file", f)

d = {
    "person":
        {"name": "Gregor"},
    "author": "{person.name}"
}

with open('data.yaml', 'w') as file:
    documents = yaml.dump(d, file)

f.load(content=filename)
print ("Type Load from file", f)

f.load(content=str(d))
print ("Type Load from string", f)

f.load(content=d)
print ("Type Load from dict", f)

"""


def key_prefix_replace(d, prefix, new_prefix=""):
    """replaces the list of prefix in keys of a flattened dict

    Args:
        d: the flattened dict
        prefix (list of str): a list of prefixes that are replaced with
            a new prefix. Typically this will be ""
        new_prefix: The new prefix. By default it is set to ""

    Returns:
        the dict with the keys replaced as specified
    """
    items = []
    for k, v in list(d.items()):
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


def flatten(d, parent_key="", sep="__"):
    """flattens the dict into a one dimensional dictionary

    Args:
        d: multidimensional dict
        parent_key: replaces from the parent key
        sep: the separation character used when fattening. the default
            is __

    Returns:
        the flattened dict
    """
    # http://stackoverflow.com/questions/6027558/flatten-nested-python-dictionaries-compressing-keys
    if type(d) == list:
        flat = []
        for entry in d:
            flat.append(flatten(entry, parent_key=parent_key, sep=sep))
        return flat
    else:
        items = []
        for k, v in list(d.items()):
            new_key = parent_key + sep + k if parent_key else k

            if isinstance(v, collections.abc.MutableMapping):
                items.extend(list(flatten(v, new_key, sep=sep).items()))
            else:
                items.append((new_key, v))

        return dict(items)


class FlatDict(dict):
    """A data structure to manage a flattened dict. It is initialized by passing
    the dict at time of initialization.
    """

    @property
    def dict(self):
        """returns the dict

        Returns:
            dict
        """
        return self.__dict__

    def __init__(self, d=None, expand=["os.", "cm.", "cloudmesh."], sep="__"):
        """initializes the flat dics

        Args:
            d: the dict data
            sep: The character used to indicate an hirachie a__b
        """
        if d is None:
            d = {}
        self.__dict__ = flatten(d, sep=sep)
        self.sep = sep
        if "all" in expand:
            self.expand_os = True
            self.expand_cloudmesh = True
            self.expand_cm = True
        else:
            self.expand_os = "os." in expand
            self.expand_cloudmesh = "cloudmesh." in expand
            self.expand_cm = "cm." in expand

    def __setitem__(self, key, item):
        """sets an item at a key

        Args:
            key: this is the key
            item: this is the item to be set
        """
        self.__dict__[key] = item

    def __getitem__(self, key):
        """gets an item form the key

        Args:
            key: the key

        Returns:
            the value
        """
        return self.__dict__[key]

    def __repr__(self):
        return repr(self.__dict__)

    def __str__(self):
        """The string representation of the dict

        Returns:
            str
        """
        return str(self.__dict__)

    def __len__(self):
        """number of elements in the dict

        Returns:
            int
        """
        return len(self.__dict__)

    def __delitem__(self, key):
        """delete the specified item

        Args:
            key: key of the item

        Returns:
            dict with the elementremoved
        """
        del self.__dict__[key]

    def keys(self):
        """returns the keys

        Returns:
            list of keys
        """
        return list(self.__dict__.keys())

    def values(self):
        """list of all values

        Returns:
            list
        """
        return list(self.__dict__.values())

    # def __cmp__(self, dictionary):
    #     """
    #     deprecated
    #     """
    #     return cmp(self.__dict__, dictionary)

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

    def search(self, key, value=None):
        """returns from a flatdict all keys that match the given pattern and
        have the given value. If the value None is specified or ommitted, all
        keys are returned regardless of value.

        Example:

            search("cloudmesh.cloud.*.cm.active", True)

        Args:
            key: The key pattern to be searched (given as regex)
            value: The value

        Returns:
            keys matching the vakue in flat dict format.
        """
        flat = FlatDict(self.__dict__, sep=".")
        r = re.compile(key)
        result = list(filter(r.match, flat))
        if value is None:
            found = result
        else:
            found = []
            for entry in result:
                if str(flat[entry]) == str(value):
                    found.append(entry)
        return found

    # Modified idea from
    # https://stackoverflow.com/questions/50607128/creating-a-nested-dictionary-from-a-flattened-dictionary
    def unflatten(self):
        """unflattens the falt dict bac to a regular dict

        Returns:
        """
        result = {}
        for k, v in self.__dict__.items():
            self._unflatten_entry(k, v, result)
        return result

    def _unflatten_entry(self, k, v, out):
        k, *rest = k.split(self.sep, 1)
        if rest:
            self._unflatten_entry(rest[0], v, out.setdefault(k, {}))
        else:
            out[k] = v

    def loadf(self, filename=None, sep="."):
        config = read_config_parameters(filename=filename)
        self.__init__(config, sep=sep)

    def loads(self, content=None, sep="."):
        config = read_config_parameters_from_string(content=content)
        self.__init__(config, sep=sep)

    def loadd(self, content=None, sep="."):
        config = read_config_parameters_from_dict(content=content)
        self.__init__(config, sep=sep)

    def load(self, content=None, expand=True, sep="."):
        """This function reads in the dict based on the values and types provided
        If the filename is provided its read from the filename
        If content is a string the string will be converted from yaml to a dict
        If a dict is provided the dict is read

        Args:
            content
            expand
            sep

        Returns:

        """
        if content is None:
            config = None
            self.loads(config)
        elif type(content) == dict:
            self.loadd(content=content, sep=".")
        elif os.path.isfile(str(content)):
            print("file")
            self.loadf(filename=content, sep=".")
        elif type(content) == str:
            self.loads(content=content, sep=".")
        else:
            config = None
            self.__init__(config, sep=sep)
        e = expand_config_parameters(
            flat=self.__dict__,
            expand_yaml=True,
            expand_os=self.expand_os,
            expand_cloudmesh=self.expand_cloudmesh or self.expand_cm,
        )
        self.__dict__ = e

    def apply_in_string(self, content):
        r = content
        for v in self.__dict__:
            try:
                r = r.replace("{" + str(v) + "}", str(self.__dict__[v]))
            except Exception as e:
                print(e)
        return r

    def apply(self, content, write=True):
        """converts a string or the contents of a file with the
        values of the flatdict

        Args:
            write (boolean): if a file is specified write determins if
                the old file is overwritten in place
            content

        Returns:

        """

        if content is None:
            return None
        elif os.path.isfile(str(content)):
            data = readfile(content)
            result = self.apply_in_string(data)
            if write:
                writefile(content, result)
            return result
        elif type(content) == str:
            return self.apply_in_string(content)
        else:
            return None


class FlatDict2(object):
    primitive = (int, str, bool, str, bytes, dict, list)

    @classmethod
    def is_primitive(cls, thing):
        return type(thing) in cls.primitive

    @classmethod
    def convert(cls, obj, flatten=True):
        """This function converts object into a Dict optionally Flattening it

        Args:
            obj: Object to be converted
            flatten: boolean to specify if the dict has to be flattened
        :return dict: the dict of the object (Flattened or Un-flattened)
        """
        dict_result = cls.object_to_dict(obj)
        if flatten:
            dict_result = FlatDict(dict_result)
        return dict_result

    @classmethod
    def object_to_dict(cls, obj):
        """This function converts Objects into Dictionary"""
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


def read_config_parameters(filename=None, d=None):
    """This file reads in configuration parameters defined in a yaml file and
    produces a flattend dict. It reads in the yaml date from a filename and/or
    a string.  If both are specified the data in the filename will be read first
    and updated with the string.

    s = '''
    experiment:
       epoch: 1
       learning_rate: 0.01
       gpu: a100
    '''

    once read in it returns the flattened dict. To just load from a string use

    config = read_config_parameters(d=s)
    print (config)

    {'experiment.epoch': 1,
     'experiment.learning_rate': 0.01,
     'experiment.gpu': 'a100'}

    Args:
        filename (string): The filename to read the yaml data from if
            the filename is not None
        d (string): The yaml data includes in a string. That will be
            added to the dict

    Returns:
        dict: the flattned dict
    """
    if filename is None:
        config = {}
    else:
        config = readfile(filename)
        config = yaml.safe_load(config)
    if d is not None:
        data = yaml.safe_load(d)
        config.update(data)
    config = flatten(config, sep=".")
    return config


def read_config_parameters_from_string(content=None, d=None):
    """This file reads in configuration parameters defined in a yaml file and
    produces a flattend dict. It reads in the yaml date from a filename and/or
    a string.  If both are specified the data in the filename will be read first
    and updated with the string.

    s = '''
    experiment:
       epoch: 1
       learning_rate: 0.01
       gpu: a100
    '''

    once read in it returns the flattened dict. To just load from a string use

    config = read_config_parameters(d=s)
    print (config)

    {'experiment.epoch': 1,
     'experiment.learning_rate': 0.01,
     'experiment.gpu': 'a100'}

    Args:
        content (string): The filename to read the yaml data from if the
            filename is not None
        d (string): The yaml data includes in a string. That will be
            added to the dict

    Returns:
        dict: the flattned dict
    """
    if content is None:
        config = {}
    else:
        print()
        print(content)
        print()
        config = yaml.safe_load(content)

        print(config)
    if d is not None:
        data = yaml.safe_load(d)
        config.update(data)
    config = flatten(config, sep=".")
    return config


def read_config_parameters_from_dict(content=None, d=None):
    """
    Args:
        content
        d (string): The yaml data includes in a string. That will be
            added to the dict
        filename (string): The filename to read the yaml data from if
            the filename is not None

    Returns:
        dict: the flattned dict

    This file reads in configuration parameters defined in a yaml file and
    produces a flattend dict. It reads in the yaml date from a filename and/or
    a string.  If both are specified the data in the filename will be read first
    and updated with the string.

    s = '''
    experiment:
       epoch: 1
       learning_rate: 0.01
       gpu: a100
    '''

    once read in it returns the flattened dict. To just load from a string use

    config = read_config_parameters(d=s)
    print (config)

    {'experiment.epoch': 1,
     'experiment.learning_rate': 0.01,
     'experiment.gpu': 'a100'}

    """
    if content is None:
        config = {}
    else:
        print()
        print(content)
        print()
        config = dict(content)
        print(config)
    if d is not None:
        data = yaml.safe_load(d)
        config.update(data)
    config = flatten(config, sep=".")
    return config


def expand_config_parameters(
    flat=None,
    expand_yaml=True,
    expand_os=True,
    expand_cloudmesh=True,
    debug=False,
    depth=100,
):
    """expands all variables in the flat dict if they are specified in the values of the flatdict.

    Args:
        flat (FlatDict): The flat dict
        expand_yaml
        expand_os
        expand_cloudmesh
        depth (int): the levels of recursive {variables} to replace

    Returns:
        dict: the dict with th ereplaced values

    from cloudmesh.common.util import readfile
    from cloudmesh.common.FlatDict import read_config_parameters, flatten, expand_config_parameters
    from cloudmesh.common.util import banner
    from pprint import pprint

    filename = "config.yaml"

    config = read_config_parameters(filename=filename)

    pprint (config)

    banner("CONFIGURATION")
    print (type(config))
    print (config)

    config = expand_config_parameters(config)

    pprint (type(config))
    """
    if flat is None:
        config = {}
    else:
        txt = json.dumps(flat)

        values = ""
        for variable in flat.keys():
            name = "{" + variable + "}"
            value = flat[variable]
            values += " " + str(value)

        if expand_yaml:
            found = True
            for i in range(0, depth):
                for variable in flat.keys():
                    name = "{" + variable + "}"
                    value = flat[variable]
                    if variable in values:
                        if debug:
                            print("found", variable, "->", value)
                        txt = txt.replace(name, str(value))

        if "{os." in values and expand_os:
            for variable in os.environ:
                if variable != "_":
                    name = "{os." + variable + "}"
                    value = os.environ[variable]

                    if name in values:
                        if debug:
                            print("found", variable, "->", value)
                        txt = txt.replace(name, str(value))

        cm_variables = Variables()

        if "{cloudmesh." in values and expand_cloudmesh:
            for variable in cm_variables:
                if variable != "_":
                    name = "{cloudmesh." + variable + "}"
                    value = cm_variables[variable]
                    if variable in values:
                        if debug:
                            print("found", variable, "->", value)
                        txt = txt.replace(name, str(value))

        if "{cm." in values and expand_cloudmesh:
            for variable in cm_variables:
                if variable != "_":
                    name = "{cm." + variable + "}"
                    value = cm_variables[variable]
                    if variable in values:
                        if debug:
                            print("found", variable, "->", value)
                        txt = txt.replace(name, str(value))

        config = json.loads(txt)

        if "eval(" in values:
            for variable in config.keys():
                name = "{" + variable + "}"
                value = config[variable]
                if type(value) == str and "eval(" in value:
                    value = value.replace("eval(", "").strip()[:-1]
                    if debug:
                        print("found", variable, "->", value)
                    value = eval(value)
                    config[variable] = value
                    # txt = txt.replace(name, str(value))

    return config


"""


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

"""
