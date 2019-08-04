# epoch_parser

CLI application for converting Unix timestamp to human readable timestamp in local timezone

This Python application is written for Python 3.7+.


## Usage

### 1. Input file

Specify `-f` optional argument and provide a filepath. The input file should have one unix timestamp (in milliseconds) per line.

```bash
python epoch_parser.py -f input.txt
```

### 2. Standard input

Specify `-ts` optional argument and provide in unix timestamp in milliseconds.

```bash
# an arbitary unix timestamp
python epoch_parser.py -ts 1564791980702

# current timestamp (macOS)
python epoch_parser.py -ts `date +%s000`

# current timestamp (Linux)
python epoch_parser.py -ts `date +%s%3N`

```


## Contribution

See an area for improvement, please open an issue or send a PR. :-)
