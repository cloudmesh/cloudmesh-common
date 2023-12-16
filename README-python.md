# Python INstalation

## Python 3.12.1

```bash
local>
  wget https://www.python.org/ftp/python/3.12.1/Python-3.12.1.tar.xz
  tar xvf Python-3.12.1.tar.xz 
  cd Python-3.12.1/
  ./configure --enable-optimizations
  sudo make -j16 && sudo make altinstall
  python3.12 --version && pip3.12 --version
```

