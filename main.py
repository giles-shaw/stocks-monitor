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


def _handle_input(data, key):
    if key in ("q", "Q"):
        raise urwid.ExitMainLoop()
    if key in [str(i) for i in range(len(FIELDS))]:
        data.sort_by_col = FIELDS[int(key)]


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
        self.data = pd.DataFrame([])
        self.data_str = [[("bold", c)] for c in FIELDS]
        self.sort_by_col = None

    def get_data(self):
        r = requests.get(
            IEX_BATCH_URL, params={"symbols": ",".join(
                self.symbols), "types": "quote"}
        )
        flattened = {k: v["quote"] for k, v in r.json().items()}
        return pd.DataFrame.from_dict(flattened, orient="index")[FIELDS]

    def get_sorted_data(self):
        if self.sort_by_col:
            return self.data.sort_values(
                by=self.sort_by_col,
                ascending=(
                    True if self.data[self.sort_by_col].dtype == "object" else False
                ),
            )
        else:
            return self.data

    def get_data_str(self):
        df_str = self.data.applymap(format_entry)

        return [[("bold", c)] + df_str[c].tolist() for c in list(df_str)]

    def get_fake_data(self):

        return self.data.applymap(
            lambda e: e + random.normal(0, 0.1) if isinstance(e, Number) else e
        )

    def update_loop(self, delay=5):
        while True:
            self.data = self.get_data()
            self.data = self.get_sorted_data()
            self.data_str = self.get_data_str()
            sleep(delay)


def refresh(loop: urwid.MainLoop, args):

    data, columns = args

    # Not always guaranteed that this is atomic, so code need not be
    # threadsafe.
    new_values = data.data_str

    str_data = [urwid.Text(c) for c in new_values]
    columns.contents = [(c, columns.options("pack")) for c in str_data]

    loop.set_alarm_in(1, refresh, (data, columns))


def gui(data: Data):

    palette = [("bold", "light red,bold", "default")]

    str_data = dict((field, urwid.Text("")) for field in FIELDS)

    columns = urwid.Columns([("pack", v)
                             for c, v in str_data.items()], dividechars=1)
    fill = urwid.Filler(columns, "top")

    def handle_input(key):
        return _handle_input(data, key)

    loop = urwid.MainLoop(fill, palette=palette, unhandled_input=handle_input)
    loop.set_alarm_in(0, refresh, (data, columns))
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
