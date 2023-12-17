###############################################################
# pytest -v --capture=no  tests/test_flatdict.py
# pytest -v tests/test_flatdict.py
# npytest -v --capture=no  tests/test_flatdict..py::Test_flatdict.test_001
###############################################################

import os
from pprint import pprint

import pytest
import yaml
from cloudmesh.common.FlatDict import FlatDict
from cloudmesh.common.FlatDict import expand_config_parameters
from cloudmesh.common.FlatDict import flatten
from cloudmesh.common.util import HEADING
from cloudmesh.common.util import writefile, readfile, banner


# noinspection PyPep8Naming
@pytest.mark.incremental
class Test_Flatdict:

    def setup_method(self):
        self.d = {
            'cloud': 'india',
            'update': '2015-06-18 22:11:48 UTC',
            'user': 'gregor',
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

        self.vm = {
            'extra': {'access_ip': '',
                      'availability_zone': 'nova',
                      'config_drive': '',
                      'created': '2015-06-19T00:06:58Z',
                      'disk_config': 'MANUAL',
                      'flavorId': '1',
                      'hostId': '',
                      'imageId': 'abcd',
                      'key_name': None,
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
        pass

    def test_flatten(self):
        HEADING()
        f = flatten(self.d)
        pprint(f)
        assert f['extra__minDisk'] == 40

    def test_FlatDict(self):
        HEADING()

        f = FlatDict(self.d)
        pprint(f.dict)
        pprint(f.__dict__)
        print(f['user'])
        print(f['extra__created'])
        print(f.user)
        print(f.extra__created)

        f.user = 'GREGOR'
        assert f.user == 'GREGOR'
        assert f['extra__minDisk'] == 40

    def test_unflatten(self):
        HEADING()

        f = FlatDict(self.d, sep=".")
        pprint(f.dict)
        pprint(f.__dict__)

        pprint(f.unflatten())

        # print(f['user'])
        # print(f['extra__created'])
        # print(f.user)
        # print(f.extra__created)
        #
        # f.user = 'GREGOR'
        # assert f.user == 'GREGOR'
        # assert f['extra__minDisk'] == 40

    def test_expand_yaml_file(self):
        HEADING()

        config = {
            "a": 2,
            "b": "test-{a}",
            "c": "eval(3*{a})"
        }
        # config = read_config_parameters(filename=filename)
        config = expand_config_parameters(config)

        pprint(config)

        assert config["b"] == "test-" + str(config["a"])
        assert config["c"] == 6

    def test_apply_str(self):
        data = {
            "a": 2,
            "b": "test-{a}",
            "c": "eval(3*{a})"
        }

        config = FlatDict()
        config.load(content=data)

        # config = read_config_parameters(filename=filename)
        # config = expand_config_parameters(config)

        pprint("config:")
        print(config)

        assert config["b"] == "test-" + str(config["a"])
        assert config["c"] == 6

        s = "a={a} {unkown}"

        result = config.apply(s)

        banner("converted")
        print(result)

        assert result == "a=2 {unkown}"

    def test_apply_file(self):
        HEADING()

        config = {
            "a": 2,
            "b": "test-{a}",
            "c": "eval(3*{a})",
            "test": {
                "a": "a",
                "b": '{a}'}
        }

        filename = "/tmp/test.yaml"
        with open(filename, "w") as f:
            yaml.dump(config, f)

        config = FlatDict()
        config.load(content=filename)

        # config = read_config_parameters(filename=filename)
        # config = expand_config_parameters(config)

        print("config:")
        pprint(config)

        assert config["b"] == "test-" + str(config["a"])
        assert config["c"] == 6

        s = "a={a} {unkown}"
        name = ".tmp/a.txt"
        writefile(name, s)
        content = readfile(name)
        print (content)

        result = config.apply(name)
        print()
        print(result)

        content = readfile(name).strip()

        banner("converted")
        print(content)

        assert result == "a=2 {unkown}"
        assert content == result

    def test_config_in_yaml(self):
        HEADING()

        config = FlatDict(expand=["os.", "cm.", "cloudmesh."])
        config .load("tests/config.in.yaml")

        print("config:")
        pprint(dict(config))

