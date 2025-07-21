# JAILMAN

JAILMAN - a simple API for bastille jail manager (https://bastillebsd.org)

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Todo](#todo)
- [License](#license)

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
- add other actions besides start/stop/restart
- tidy up template files
- 

## Usage
For now, the service needs to be run manually, but it is self-contained.
```sh
./jailman.py
```

## License

BSD 3 clause License
See `LICENSE` file for full text.


