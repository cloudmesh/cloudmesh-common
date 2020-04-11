# Changelog

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

