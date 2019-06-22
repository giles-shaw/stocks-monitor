"""
CLI for stocks_monitor.
"""
import argparse
from pathlib import Path
from typing import Callable, Iterator

import pandas as pd
import toml

from stocks_monitor.data import data_feed, fake_data_feed
from stocks_monitor.main import monitor

CONFIG_PATH = Path.home() / Path(".stocks-monitor/config.toml")
TOKEN_PATH = Path.home() / Path(".stocks-monitor/credentials.toml")

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
        default=tuple(),
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

    kwargs = {"symbols": args.symbols, "fields": FIELDS}
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, "r") as f:
            kwargs = {**kwargs, **toml.load(f)}
    with open(TOKEN_PATH, "r") as f:
        kwargs["token"] = toml.load(f)["iex_publishable_token"]

    stocks_feed: Callable[
        ..., Iterator[pd.DataFrame]
    ] = fake_data_feed if args.test else data_feed
    monitor(stocks_feed(**kwargs))


if __name__ == "__main__":
    cli()
