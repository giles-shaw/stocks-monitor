"""
CLI for stocks_monitor.
"""
import argparse
from pathlib import Path
from typing import Any, List, Dict

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


class SymbolNotFoundError(Exception):
    pass


def get_symbols(args: List[str], path: Path) -> List[str]:

    if args:
        return args
    elif path.is_file():
        with open(path, "r") as f:
            try:
                return toml.load(f)["symbols"]
            except KeyError:
                pass
    raise SymbolNotFoundError


def get_fields(path: Path) -> Dict[str, str]:

    if path.is_file():
        with open(path, "r") as f:
            d = toml.load(f).get("fields", {})
        if d:
            return d
    return FIELDS


def cli() -> None:

    parser = argparse.ArgumentParser(
        description="display real time market information for stocks"
    )
    parser.add_argument(
        "-s",
        "--symbols",
        nargs="+",
        type=str,
        help="stock ticker symbols to display",
    )
    args = parser.parse_args()

    path = Path.home() / Path(".stocks-monitor.conf")
    stocks_monitor(get_symbols(args.symbols, path), get_fields(path))


if __name__ == "__main__":
    cli()
