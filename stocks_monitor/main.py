from functools import partial
from numbers import Number
from pathlib import Path
from sys import argv
from threading import Thread
from time import sleep
from typing import Any, List, Tuple

import pandas as pd
import requests
import toml
import urwid
from numpy import random

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"

FIELDS = [
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
FIELDS = {**dict([(f, f) for f in FIELDS]), **ALIASES}


def sort_data(data: pd.DataFrame, sort_key: int) -> pd.DataFrame:

    if sort_key:
        try:
            field = list(data)[sort_key]
            return data.sort_values(
                by=field,
                ascending=(True if data[field].dtype == "object" else False),
            )
        except IndexError:
            pass

    return data


def format_entry(e: Any) -> str:

    if isinstance(e, Number):
        return format_number(e)
    else:
        return "\n" + str(e)


def format_number(e: int) -> str:
    if e > 10 ** 12:
        return "\n" + f"{e / (10 ** 12):.2f}" + "T"
    elif e > 10 ** 9:
        return "\n" + f"{e / (10 ** 9):.2f}" + "B"
    elif e > 10 ** 6:
        return "\n" + f"{e / (10 ** 6):.2f}" + "M"
    elif isinstance(e, float):
        return "\n" + f"{e:.2f}"
    elif isinstance(e, int):
        return "\n" + str(e)


def format_data(data: pd.DataFrame) -> List[urwid.Text]:

    df_str = data.applymap(format_entry)
    text_cols = [[("bold", c)] + df_str[c].tolist() for c in list(df_str)]

    return [urwid.Text(tc) for tc in text_cols]


def process_for_gui(data: pd.DataFrame, sort_key: int) -> List[urwid.Text]:

    return format_data(sort_data(data, sort_key))


class Data:
    def __init__(self, symbols: List[str]) -> None:
        self.symbols = symbols
        self.data = pd.DataFrame([], columns=list(FIELDS.values()))

    def get_data(self) -> pd.DataFrame:
        r = requests.get(
            IEX_BATCH_URL,
            params={"symbols": ",".join(self.symbols), "types": "quote"},
        )
        flattened = {k: v["quote"] for k, v in r.json().items()}

        return pd.DataFrame.from_dict(flattened, orient="index").rename(
            FIELDS, axis="columns"
        )[list(FIELDS.values())]

    def get_fake_data(self) -> pd.DataFrame:
        def noise(e):
            if isinstance(e, Number):
                return e + random.normal(0, 0.1)
            return e

        return self.data.applymap(noise)

    def update_loop(self, fake=True, delay=5):
        while True:
            self.data = self.get_data()
            if fake:
                self.data = self.get_fake_data()
            sleep(delay)


class UserInput:
    def __init__(self) -> None:
        self.sort_key = None


def refresh(
    loop: urwid.MainLoop, args: Tuple[pd.DataFrame, urwid.Columns, UserInput]
) -> None:

    data, columns, user_input = args

    # Don't know if this is threadsafe
    columns.contents = [
        (c, columns.options("pack"))
        for c in process_for_gui(data.data, user_input.sort_key)
    ]

    loop.set_alarm_in(0.5, refresh, (data, columns, user_input))


def handle_input(user_input: UserInput, key: int) -> None:

    if key in ("q", "Q"):
        raise urwid.ExitMainLoop()
    try:
        user_input.sort_key = int(key)
    except ValueError:
        pass


def gui(data: Data) -> None:

    columns = urwid.Columns(
        [("pack", urwid.Text(""))] * len(FIELDS), dividechars=3
    )
    fill = urwid.Filler(columns, "top")

    user_input = UserInput()

    loop = urwid.MainLoop(
        fill,
        palette=[("bold", "light red,bold", "default")],
        unhandled_input=partial(handle_input, user_input),
    )
    loop.set_alarm_in(0, refresh, (data, columns, user_input))
    loop.run()


def stocks_monitor(symbols: List[str]) -> None:

    data = Data(symbols)

    Thread(target=data.update_loop, daemon=True).start()
    gui(data)


def get_symbols(argv: List[Any]) -> List[str]:

    path = Path.home() / Path(".stocks-monitor.conf")
    if path.is_file():
        with open(path, "r") as f:
            return toml.load(f).get("symbols", [])
    else:
        return argv[1:]


def cli() -> None:

    stocks_monitor(get_symbols(argv))


if __name__ == "__main__":
    cli()
