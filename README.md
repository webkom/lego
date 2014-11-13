# LEGO Er Ganske Oppdelt
[![Build status](https://ci.frigg.io/badges/webkom/lego/)](https://ci.frigg.io/webkom/lego/)

```bash
$ make
  dev        - install dev requirements
  prod       - install prod requirements
  venv       - create virtualenv venv-folder
  production - deploy production (used by chewie)
```

## Development
### Mac
```bash
brew update
brew install python3 postgresql
make lego/settings/local.py
make venv # Or create a venv your preferred way
source venv/bin/activate
make dev
```
