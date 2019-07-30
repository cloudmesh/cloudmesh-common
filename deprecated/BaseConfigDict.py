"""Some simple yaml file reader"""

from __future__ import print_function

import ast
import json
import os
import stat
import sys
from collections import OrderedDict
from pprint import pprint
from string import Template

import simplejson
import oyaml as yaml

from cloudmesh.common.console import Console
from cloudmesh.common.error import Error
from cloudmesh.common.locations import config_file
from cloudmesh.common.util import backup_name, path_expand

import warnings

# warnings.simplefilter('ignore', yaml.error.UnsafeLoaderWarning)
# Logger dependency not to be there in utility
# log = LOGGER(__file__)
package_dir = os.path.dirname(os.path.abspath(__file__))
attribute_indent = 4


def check_file_for_tabs(filename, verbose=True):
    """identifies if the file contains tabs and returns True if it
    does. It also prints the location of the lines and columns. If
    verbose is set to False, the location is not printed.

    :param verbose: if true prints information about issues
    :param filename: the filename
    :rtype: True if there are tabs in the file
    """
    file_contains_tabs = False
    with open(filename) as f:
        lines = f.read().split("\n")

    line_no = 1
    for line in lines:
        if "\t" in line:
            file_contains_tabs = True
            location = [
                i for i in range(len(line)) if line.startswith('\t', i)]
            if verbose:
                Console.error("Tab found in line {} and column(s) {}"
                              .format(line_no,
                                      str(location).replace("[", "").replace(
                                          "]", "")),
                              traceflag=False)
        line_no += 1
    return file_contains_tabs


# http://stackoverflow.com/questions/5121931/in-python-how-can-you-load-yaml-mappings-as-ordereddicts

# noinspection PyPep8Naming
def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
    """
    Loads an ordered dict into a yaml while preserving the order

    :param stream: the name of the stream
    :param Loader: the yam loader (such as yaml.SafeLoader)
    :param object_pairs_hook: the ordered dict
    """

    # noinspection PyClassHasNoInit
    class OrderedLoader(Loader):
        """
        A helper class to define an Ordered Loader
        """
        pass

    def construct_mapping(loader, node):
        """
        construct a flattened node mapping
        :param loader: the loader
        :param node: the node dict
        :return: 
        """
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    return yaml.load(stream, OrderedLoader)


# usage example:
# ordered_load(stream, yaml.SafeLoader)


# noinspection PyPep8Naming
def ordered_dump(data, stream=None, Dumper=yaml.Dumper, **keywords):
    """
    writes the dict into an ordered yaml.

    :param data: The ordered dict
    :param stream: the stream
    :param Dumper: the dumper such as yaml.SafeDumper
    """

    # noinspection PyClassHasNoInit
    class OrderedDumper(Dumper):
        """
        A helper class to create an ordered dump
        """
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            data.items())

    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **keywords)


# usage:
# ordered_dump(data, Dumper=yaml.SafeDumper)


def read_yaml_config(filename, check=True, osreplace=True, exit=True):
    """
    reads in a yaml file from the specified filename. If check is set to true
    the code will fail if the file does not exist. However if it is set to
    false and the file does not exist, None is returned.

    :param exit: if true is exist with sys exit
    :param osreplace: if true replaces environment variables from the OS
    :param filename: the file name
    :param check: if True fails if the file does not exist,
                  if False and the file does not exist return will be None
    """
    location = filename
    if location is not None:
        location = path_expand(location)

    if not os.path.exists(location) and not check:
        return None

    if check and os.path.exists(location):

        # test for tab in yaml file
        if check_file_for_tabs(location):
            log.error("The file {0} contains tabs. yaml "
                      "Files are not allowed to contain tabs".format(location))
            sys.exit()
        result = None
        try:

            if osreplace:
                result = open(location, 'r').read()
                t = Template(result)
                result = t.substitute(os.environ)

                # data = yaml.safe_load(result)
                data = ordered_load(result, yaml.SafeLoader)
            else:
                f = open(location, "r")

                # data = yaml.safe_load(f)

                data = ordered_load(result, yaml.SafeLoader)
                f.close()

            return data
        except Exception as e:
            log.error(
                "The file {0} fails with a yaml read error".format(filename))
            Error.traceback(e)
            sys.exit()

    else:
        log.error("The file {0} does not exist.".format(filename))
        if exit:
            sys.exit()

    return None


class OrderedJsonEncoder(simplejson.JSONEncoder):
    """
    Manage ordered Json Objects
    """
    indent = attribute_indent

    def encode(self, o, depth=0):
        """
        encode the json object at given depth
        :param o: the object
        :param depth: the depth
        :return: the json encoding
        """
        if isinstance(o, OrderedDict):
            return "{" + ",\n ".join([self.encode(k) + ":" +
                                      self.encode(v, depth + 1)
                                      for (k, v) in o.items()]) + "}\n"
        else:
            return simplejson.JSONEncoder.encode(self, o)


def custom_print(data_structure, indent):
    """
    prints a given data structure such as a dict or ordered dict at a given indentation level
    :param data_structure: 
    :param indent: 
    :return: 
    """
    for key, value in data_structure.items():
        print("\n%s%s:" % (' ' * attribute_indent * indent, str(key)), end=' ')
        if isinstance(value, OrderedDict):
            custom_print(value, indent + 1)
        elif isinstance(value, dict):
            custom_print(value, indent + 1)
        else:
            print("%s" % (str(value)), end=' ')


class BaseConfigDict(OrderedDict):
    """
    A class to obtain an OrderedDict from a yaml file.
    """

    def _set_filename(self, filename):
        """
        Sets the filename to be used.

        :param filename: the filename
        """
        self['filename'] = filename
        self['location'] = path_expand(self["filename"])

    def __init__(self, *args, **kwargs):
        """
        The initialization method
        """
        OrderedDict.__init__(self, *args, **kwargs)

        if 'filename' in kwargs:
            self._set_filename(kwargs['filename'])
        else:
            log.error("filename not specified")
            # sys.exit()

        if os.path.isfile(self['location']):
            self.load(self['location'])

        # print ("ATTRIBUTE", attribute)
        for attribute in ['prefix']:
            if attribute in kwargs:
                self[attribute] = kwargs[attribute]
            else:
                self[attribute] = None

        self._update_meta()

    def _update_meta(self):
        """
        internal function to define the metadata regarding filename, location,
        and prefix.
        """
        for v in ["filename", "location", "prefix"]:
            if "meta" not in self:
                self["meta"] = {}
            self["meta"][v] = self[v]
            del self[v]

    def read(self, filename):
        """
        Loads the information in the yaml file. It is the same as load and is
        used for compatibility reasons.

        :param filename: the name of the yaml file
        """
        self.load(filename)

    def load(self, filename):
        """
        Loads the yaml file with the given filename.

        :param filename: the name of the yaml file
        """

        self._set_filename(filename)

        if os.path.isfile(self['location']):
            # d = OrderedDict(read_yaml_config(self['location'], check=True))
            d = read_yaml_config(self['location'], check=True)
            with open(self['location']) as myfile:
                document = myfile.read()
            x = yaml.load(document, Loader=yaml.FullLoader)
            try:
                self.update(d)
            except:
                print("ERROR: can not find", self["location"])
                sys.exit()
        else:
            print(
                "Error while reading and updating the configuration file {:}".format(
                    filename))

    def make_a_copy(self, location=None):
        """
        Creates a backup of the file specified in the location. The backup
        filename  appends a .bak.NO where number is a number that is not yet
        used in the backup directory.

        TODO: This function should be moved to another file maybe XShell

        :param location: the location of the file to be backed up
        """
        import shutil
        destination = backup_name(location)
        shutil.copyfile(location, destination)

    def write(self, filename=None, output="dict",
              attribute_indent=attribute_indent):
        """
        This method writes the dict into various output formats. This includes a dict,
        json, and yaml

        :param filename: the file in which the dict is written
        :param output: is a string that is either "dict", "json", "yaml"
        :param attribute_indent: character indentation of nested attributes in
        """
        if filename is not None:
            location = path_expand(filename)
        else:
            location = self['meta']['location']

            # with open('data.yml', 'w') as outfile:
            #    outfile.write( yaml.dump(data, default_flow_style=True) )

        # Make a backup
        self.make_a_copy(location)

        f = os.open(location, os.O_CREAT | os.O_TRUNC |
                    os.O_WRONLY, stat.S_IRUSR | stat.S_IWUSR)
        if output == "json":
            os.write(f, self.json())
        elif output in ['yml', 'yaml']:
            # d = dict(self)
            # os.write(f, yaml.dump(d, default_flow_style=False))
            os.write(f, ordered_dump(OrderedDict(self),
                                     Dumper=yaml.SafeDumper,
                                     default_flow_style=False,
                                     indent=attribute_indent))
        elif output == "print":
            os.write(f, str(custom_print(self, attribute_indent)))
        else:
            os.write(f, self.dump())
        os.close(f)

    def error_keys_not_found(self, keys):
        """
        Check if the requested keys are found in the dict.

        :param keys: keys to be looked for
        """
        try:
            log.error("Filename: {0}".format(self['meta']['location']))
        except:
            log.error("Filename: {0}".format(self['location']))
        log.error("Key '{0}' does not exist".format('.'.join(keys)))
        indent = ""
        last_index = len(keys) - 1
        for i, k in enumerate(keys):
            if i == last_index:
                log.error(indent + k + ": <- this value is missing")
            else:
                log.error(indent + k + ":")
            indent += "    "

    def __str__(self):
        """
        returns the json output of the dict.
        """
        return self.json()

    def json(self):
        """
        returns the json output of the dict.
        """
        return json.dumps(self, indent=attribute_indent)

    def yaml(self):
        """
        returns the yaml output of the dict.
        """
        return ordered_dump(OrderedDict(self),
                            Dumper=yaml.SafeDumper,
                            default_flow_style=False)

    # noinspection PyPep8Naming
    def dump(self):
        """
        returns the json output of the dict.
        """
        orderedPrinter = OrderedJsonEncoder()
        return orderedPrinter.encode(self)

    def pprint(self):
        """
        uses pprint to print the dict
        """
        print(custom_print(self, attribute_indent))

    """
    def __getitem__(self, *mykeys):
        try:
            item = self.get(mykeys[0])
        except:
            self._notify_of_error(mykeys)
            sys.exit()
        return item
    """

    def get(self, *keys):
        """
        returns the dict of the information as read from the yaml file. To
        access the file safely, you can use the keys in the order of the
        access.
        Example: get("provisioner","policy") will return the value of
        config["provisioner"]["policy"] from the yaml file if it does not exists
        an error will be printing that the value does not exists. Alternatively
        you can use the . notation e.g. get("provisioner.policy")
        """
        if keys is None:
            return self

        if "." in keys[0]:
            keys = keys[0].split('.')
        element = self
        for v in keys:
            try:
                element = element[v]
            except KeyError:
                self.error_keys_not_found(keys)
                # sys.exit()
        return element

    def set(self, value, *keys):
        """
        Sets the dict of the information as read from the yaml file. To access
        the file safely, you can use the keys in the order of the access.
        Example: set("{'project':{'fg82':[i0-i10]}}", "provisioner","policy")
        will set the value of config["provisioner"]["policy"] in the yaml file if
        it does not exists an error will be printing that the value does not
        exists.  Alternatively you can use the . notation e.g.
        set("{'project':{'fg82':[i0-i10]}}", "provisioner.policy")
        """
        element = self

        if keys is None:
            return self

        if '.' in keys[0]:
            keys = keys[0].split(".")

        nested_str = ''.join(["['{0}']".format(x) for x in keys])
        # Safely evaluate an expression to see if it is one of the Python
        # literal structures: strings, numbers, tuples, lists, dicts, booleans,
        # and None. Quoted string will be used if it is none of these types.
        try:
            ast.literal_eval(str(value))
            converted = str(value)
        except ValueError:
            converted = "'" + str(value) + "'"
        exec("self" + nested_str + "=" + converted)
        return element

    def _update(self, keys, value):
        """Updates the selected key with the value

        Args:
            keys (str): key names e.g. cloudmesh.server.loglevel
            value (str): value to set
        """
        return self.set(value, keys)

    def attribute(self, keys):
        """
        TODO: document this method

        :param keys:
        """
        if self['meta']['prefix'] is None:
            k = keys
        else:
            k = self['meta']['prefix'] + "." + keys
        return self.get(k)


if __name__ == "__main__":
    # TODO: etc not supported
    # need to create copy and work with that
    config = ConfigDict({"a": "1", "b": {"c": 3}},
                        prefix="cloudmesh.debug",
                        filename="./etc/cloudmesh_debug.yaml")

    print("PPRINT")
    print(70 * "=")
    pprint(config)

    print("PRINT")
    print(70 * "=")
    print(config.pprint())
    print(config.json())

    print(70 * "=")
    print("A =", config["a"])
    config.write(config_file("/d.yaml"), output="dict")
    config.write(config_file("/j.yaml"), output="json")
    config.write(config_file("/y.yaml"), output="yaml")

    # this does not work
    # config.write(config_file("/print.yaml"), output="print")

    print("mongo.path GET =", config.get("cloudmesh.server.mongo.path"))
    print("mongo.path ATTRIBUTE =", config.attribute("mongo.path"))

    print("get A =", config.get("a"))

    print("wrong mongo.path ATTRIBUTE =", config.attribute("mongo.path.wrong"))
    print("wrong mongo.path GET =",
          config.get("cloudmesh.server.mongo.path.wrong"))

    # print config["dummy"]
    # config["x"] = "2"
    # print config["x"]
    # print config.x
