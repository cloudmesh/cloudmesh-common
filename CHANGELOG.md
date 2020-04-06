# Changelog

- `cloudmesh.common.Parameter._expand_string`: was added to allow
  /dev/sd[a-z] expansion
- `cloudmesh.common.Parameter._expand`: populates missing SERVICE:SOURCE
  into comma separated services.
- `cloudmesh.common.Parameter.separate`: separates SERVICE:SOURCE
  This is useful for `cloudmesh-storage`
- move some of the tests that belong into cmd5 from other repos

## 4.2.50 (04/01/2020)

Intermediate Releases: 4.2.49

#### Enhancements:

- `cloudmesh.common.Shell.rmdir` uses now `shutil.rmtree`
- `cloudmesh.common.Stopwatch.benchmark` uses now tabulate
- `cloudmesh.common.sysinfo` has been improved with getattr for mem and
  uname

#### Bug Fixes:

- None

## 4.2.48 (03/30/2020)

Intermediate Releases: 4.2.47 - 4.2.34

#### Enhancements:

- parallel gather and scetter for keys
- Shell.ps is now based on psutil
- Shell.kill is now based on psutil
- Shell.ls is now using glob
- use splitlines() instead of \n

#### Bug Fixes:

- fix the parallel SSH command

