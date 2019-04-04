# Cloudmesh Common

[![image](https://img.shields.io/travis/TankerHQ/cloudmesh-common.svg?branch=master)](https://travis-ci.org/TankerHQ/cloudmesn-common)

[![image](https://img.shields.io/pypi/pyversions/cloudmesh-common.svg)](https://pypi.org/project/cloudmesh-common)

[![image](https://img.shields.io/pypi/v/cloudmesh-common.svg)](https://pypi.org/project/cloudmesh-common/)

[![image](https://img.shields.io/github/license/TankerHQ/python-cloudmesh-common.svg)](https://github.com/TankerHQ/python-cloudmesh-common/blob/master/LICENSE)


Make sure you have the newest version of pip and setup tools

```bash
$ pip install -U setuptools pip
```


This library contains a number of useful functions and APIs:

* Console

  A convenient way to print colored messages types in the terminal,
  such as errors, info, and regular messages

* Shell

  A convenient way to execute operating system commands in python

* Printer

  A convenient way to pring dictionaries and lists with repeated
  entries as tables, csv, json, yaml

* StopWatch

  A convenient way on using named timers

* dotdict

  Dictionaries in dot format

* ssh

  * managing ssh config files
  * managing authorized keys

* other util functions such as

  * generating passwords
  * banners
  * yn_choices
  * path_expansion
  * grep (simple line matching)
