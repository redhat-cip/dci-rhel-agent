# DCI RHEL Agent


## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [License](#license)
- [Contact](#contact)

## Requirements

### Distributed-CI account

You need to create your user account in the system. Please connect to
https://www.distributed-ci.io with your redhat.com SSO account.

Your user account will be created in our database the first time you connect.

There is no reliable way to automatically know your team. So please
[contact](#contact) us back when you reach this step, we will manually move
your user in the correct organisation.


## Installation

The agent comes in form of a RPM called `dci-rhel-agent`. In order to install
it one needs to install the `dci-release` package.

```bash
#> yum -y install https://packages.distributed-ci.io/dci-release.el7.noarch.rpm
#> yum -y install dci-rhel-agent
```

## Configuration


## Usage


## License

Apache License, Version 2.0 (see [LICENSE](LICENSE) file)

## Contact

Email: Distributed-CI Team  <distributed-ci@redhat.com>

IRC: #distributed-ci on Freenode
