# JAILMAN

JAILMAN - a simple API for bastille jail manager

## Table of Contents

- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)
- [Contributing](#contributing)
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

## Configuration

```sh
Edit the config.ini file.  It should be self-documenting


```


## Usage
```sh
TODO
```

## Examples

```sh
The following example is to test the API

List all jails
curl -k -H "X-API-Key:AReallyLongComplicatedSecretKey12345" "http://localhost:9191/list_jails"

Restart jail - testjail
curl -k -H "X-API-Key:AReallyLongComplicatedSecretKey12345" "http://localhost:9191/restart?jail=testjail"

```


## Contributing

PRs welcome! Fork the repo and submit a pull request.
If you find bugs, file an issue. Be nice and descriptive.

## License

MIT License (or whatever you use).
See `LICENSE` file for full text.


