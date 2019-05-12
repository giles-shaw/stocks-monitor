from functools import partial
from numbers import Number
from pathlib import Path
from sys import argv
from threading import Thread
from time import sleep
from typing import List

import pandas as pd
import requests
import toml
import urwid
from numpy import random

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"

FIELDS = ["symbol", "iexRealtimePrice",
          "open", "close", "marketCap", "peRatio"]


def handle_input(user_input, key):
    if key in ("q", "Q"):
        raise urwid.ExitMainLoop()
    if key in [str(i) for i in range(len(FIELDS))]:
        user_input.sort_key = FIELDS[int(key)]


def format_entry(e):

    if isinstance(e, str):
        return "\n" + e
    elif isinstance(e, int) or e is None:
        return "\n" + str(e)
    elif isinstance(e, float):
        return "\n" + f"{e:.2f}"
    else:
        raise NotImplementedError


class Data:
    def __init__(self, symbols):
        self.symbols = symbols
        self.data = pd.DataFrame([], columns=FIELDS)

    def get_data(self):
        r = requests.get(
            IEX_BATCH_URL, params={"symbols": ",".join(
                self.symbols), "types": "quote"}
        )
        flattened = {k: v["quote"] for k, v in r.json().items()}
        return pd.DataFrame.from_dict(flattened, orient="index")[FIELDS]

    def get_fake_data(self):

        return self.data.applymap(
            lambda e: e + random.normal(0, 0.1) if isinstance(e, Number) else e
        )

    def update_loop(self, fake=True, delay=5):
        while True:
            self.data = self.get_data()
            if fake:
                self.data = self.get_fake_data()
            sleep(delay)


def sort_data(data, sort_key):
    if sort_key:
        return data.sort_values(
            by=sort_key, ascending=(
                True if data[sort_key].dtype == "object" else False)
        )
    else:
        return data


def format_data(data):
    df_str = data.applymap(format_entry)
    text_cols = [[("bold", c)] + df_str[c].tolist() for c in list(df_str)]

    return [urwid.Text(tc) for tc in text_cols]


def process_for_gui(data, sort_key):
    return format_data(sort_data(data, sort_key))


class UserInput:
    def __init__(self):
        self.sort_key = None


def refresh(loop: urwid.MainLoop, args):

    data, columns, user_input = args

    # Not always guaranteed that this is atomic, so code need not be
    # threadsafe.
    str_data = process_for_gui(data.data, user_input.sort_key)
    columns.contents = [(c, columns.options("pack")) for c in str_data]

    loop.set_alarm_in(0.5, refresh, (data, columns, user_input))


def gui(data: Data):

    palette = [("bold", "light red,bold", "default")]

    str_data = [urwid.Text("") for field in FIELDS]

    columns = urwid.Columns([("pack", v) for v in str_data], dividechars=1)
    fill = urwid.Filler(columns, "top")

    user_input = UserInput()

    loop = urwid.MainLoop(
        fill, palette=palette, unhandled_input=partial(
            handle_input, user_input)
    )
    loop.set_alarm_in(0, refresh, (data, columns, user_input))
    loop.run()


def stocks_monitor(symbols: List[str]):

    data = Data(symbols)
    updater = Thread(target=data.update_loop, daemon=True)
    updater.start()

    gui(data)


def get_symbols(argv):

    path = Path.home() / Path(".sm.conf")
    if path.is_file():
        with open(path, "r") as f:
            return toml.load(f).get("symbols", [])
    else:
        return argv[1:]


def cli():

    stocks_monitor(get_symbols(argv))


if __name__ == "__main__":
    cli()
