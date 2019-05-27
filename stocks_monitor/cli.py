"""
CLI for stocks_monitor.
"""
from pathlib import Path
from sys import argv
from typing import Any, List

import toml

from stocks_monitor.main import stocks_monitor

IEX_KEYS = [
    "symbol",
    "iexRealtimePrice",
    "open",
    "close",
    "marketCap",
    "peRatio",
]
ALIASES = dict(
    [
        ("iexRealtimePrice", "current"),
        ("peRatio", "p/e"),
        ("marketCap", "mktCap"),
    ]
)
FIELDS = {**dict([(f, f) for f in IEX_KEYS]), **ALIASES}


def get_symbols(argv: List[Any]) -> List[str]:

    path = Path.home() / Path(".stocks-monitor.conf")
    if path.is_file():
        with open(path, "r") as f:
            return toml.load(f).get("symbols", [])
    else:
        return argv[1:]


def cli() -> None:

    stocks_monitor(get_symbols(argv), FIELDS)


if __name__ == "__main__":
    cli()
