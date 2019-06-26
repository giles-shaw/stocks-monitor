"""
CLI for stocks_monitor.
"""
import argparse
import os
from pathlib import Path
from typing import Any, Callable, Dict, Iterator

import pandas as pd
import toml

from stocks_monitor.data import data_feed, fake_data_feed
from stocks_monitor.main import monitor

XDG_CONFIG_HOME = os.environ.get("XDG_CONFIG_HOME")
SM_CONFIG = Path("stocks-monitor/config.toml")
SM_CREDENTIALS = Path("stocks-monitor/credentials.toml")

if XDG_CONFIG_HOME:
    CONFIG_PATH = Path(XDG_CONFIG_HOME) / SM_CONFIG
    CREDENTIALS_PATH = Path(XDG_CONFIG_HOME) / SM_CREDENTIALS
else:
    CONFIG_PATH = Path.home() / Path(".config") / SM_CONFIG
    CREDENTIALS_PATH = Path.home() / Path(".config") / SM_CREDENTIALS

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


def add_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
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

    return parser


def cli() -> None:

    parser = add_arguments(
        argparse.ArgumentParser(
            description="display real time market information for stocks"
        )
    )

    args = parser.parse_args()

    kwargs: Dict[str, Any] = {"fields": FIELDS}
    if CONFIG_PATH.is_file():
        with open(CONFIG_PATH, "r") as f:
            kwargs = {**kwargs, **toml.load(f)}

    if args.symbols:
        kwargs["symbols"] = args.symbols

    with open(CREDENTIALS_PATH, "r") as f:
        kwargs["token"] = toml.load(f)["iex_publishable_token"]

    stocks_feed = fake_data_feed if args.test else data_feed  # type: ignore
    monitor(stocks_feed(**kwargs))


if __name__ == "__main__":
    cli()
