# JAILMAN

JAILMAN - a simple API for bastille jail manager (https://bastillebsd.org) with example frontend

Just a simple frontend to stop/start/restart FreeBSD jails created with Bastille.  I'll probably add more functionality when I have a need for it.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Todo](#todo)
- [License](#license)

## Requirements

- Basic Python installation
- installation of bastille (bastillebsd.org / https://github.com/BastilleBSD/bastille)

## Installation

```sh
git clone https://github.com/Tim-aslat/jailman.git
cd jailman
# Optional: create a virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Alternatively you can just run the start.sh file
```sh
./start.sh
```

## Configuration

```sh
Edit the config.ini file.  It should be self-documenting

```

## Todo
- Add other actions besides start/stop/restart
- Tidy up template files
- Separate frontend templates to make it more modular (maybe, if there's a reason to)
- Add RC service option
- Daemonize process

## Usage
For now, the service needs to be run manually, but it is self-contained.
```sh
./start.sh
```

## License

BSD 3 clause License
See `LICENSE` file for full text.

