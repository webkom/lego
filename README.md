# LEGO Er Ganske Oppdelt
[![Build status](https://ci.frigg.io/badges/webkom/lego/)](https://ci.frigg.io/webkom/lego/last/)
[![Coverage status](https://ci.frigg.io/badges/coverage/webkom/lego/)](https://ci.frigg.io/webkom/lego/last/)

```bash
$ make
  development - install dev requirements, setup local.py and run migrations
  venv        - create virtualenv venv-folder
  production  - deploy production (used by chewie)
```

## Development

### Mac

Requires [Homebrew](http://brew.sh/).

```bash
brew update
brew install python3 postgresql
make venv # Or create a virtualenv your preferred way
make development
source venv/bin/activate
```
