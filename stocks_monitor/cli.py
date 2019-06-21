"""
CLI for stocks_monitor.
"""
import argparse
from pathlib import Path
from typing import List, Dict, Iterator, Callable

import pandas as pd
import toml

from stocks_monitor.data import data_feed, fake_data_feed
from stocks_monitor.main import monitor

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
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        default=False,
        help="use fake updates to test functionality when markets are closed",
    )
    args = parser.parse_args()

    config_path = Path.home() / Path(".stocks-monitor/config.toml")
    token_path = Path.home() / Path(".stocks-monitor/credentials.toml")
    symbols, fields, token = (
        get_symbols(args.symbols, config_path),
        get_fields(config_path),
        get_token(token_path),
    )

    stocks_feed: Callable[
        [List[str], Dict[str, str], str], Iterator[pd.DataFrame]
    ] = fake_data_feed if args.test else data_feed
    monitor(stocks_feed(symbols, fields, token))


def get_symbols(args: List[str], path: Path) -> List[str]:

    if args:
        return args
    with open(path, "r") as f:
        return toml.load(f)["symbols"]


def get_fields(path: Path) -> Dict[str, str]:

    try:
        with open(path, "r") as f:
            return toml.load(f)["fields"]
    except (FileNotFoundError, IsADirectoryError, KeyError):
        return FIELDS


def get_token(path: Path) -> str:

    with open(path, "r") as f:
        return toml.load(f)["iex_publishable_token"]


if __name__ == "__main__":
    cli()
