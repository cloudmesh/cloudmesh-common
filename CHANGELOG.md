# Changelog

## Changes so far in version 5

## 5.0.26

Summary of changes till 5.0.26

* add calculate disk space
* fix make pip
* Merge branch 'main' of github.com:cloudmesh/cloudmesh-common
* improve the printer
* update project urls
* add check for sudo
* add pip uninstall from package
* Merge branch 'main' of github.com:cloudmesh/cloudmesh-common
* the delete tag for github is now in cloudmesh-git
* update makefile
* Add strict editable mode to pip installation
* update docstring
* update docstrings
* Refactor Default class to include documentation
* add v5 files
* improve documentation
* convert docstrings to google format
* update bumpversion.yaml
* add strict install
* move the docker file test to future
* do for now ignore the verbose test
* print location of var file in verbose test
* improve verbose test
* improve verbose test
* change install.sh to e.sh
* moving towards toml

## 4.3.2

Intermediate releases: 4.3.1, 4.3.0

* added the new Location class to `cloudmesh.common.location` so we can
  use the OS variable `CLOUDMESH_CONFIG_DIR`
* changed `cloudmesh.common.locations` to `cloudmesh.common.location`
* `cloudmesh.common.variables.Variables.boolean` was added to allow more
  easily to set boolean variables with on and True.
* `cloudmesh.common.Parameter._expand_string`: was added to allow
  `/dev/sd[a-z]` expansion
* `cloudmesh.common.Parameter._expand`: populates missing SERVICE:SOURCE
  into comma separated services.
* `cloudmesh.common.Parameter.separate`: separates SERVICE:SOURCE
  This is useful for `cloudmesh-storage`
* move some of the tests that belong into cmd5 from other repos

## 4.2.50 (04/01/2020)

Intermediate Releases: 4.2.49

* `cloudmesh.common.Shell.rmdir` uses now `shutil.rmtree`
* `cloudmesh.common.Stopwatch.benchmark` uses now tabulate
* `cloudmesh.common.sysinfo` has been improved with getattr for mem and
  uname

## 4.2.48 (03/30/2020)

Intermediate Releases: 4.2.47 - 4.2.34

* parallel gather and scetter for keys
* Shell.ps is now based on psutil
* Shell.kill is now based on psutil
* Shell.ls is now using glob
* use splitlines() instead of \n
* fixed the parallel SSH command

