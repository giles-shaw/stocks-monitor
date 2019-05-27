from functools import partial
from numbers import Number
from pathlib import Path
from queue import Queue
from sys import argv
from threading import Thread
from time import sleep
from typing import Any, Callable, List, Optional

import pandas as pd
import requests
import toml
import urwid
from numpy import random

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"

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


def format_number(e: Any) -> str:
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
    raise ValueError


def format_data(data: pd.DataFrame) -> List[urwid.Text]:

    df_str = data.applymap(format_entry)
    text_cols = [[("bold", c)] + df_str[c].tolist() for c in list(df_str)]

    return [urwid.Text(tc) for tc in text_cols]


def process_for_gui(data: pd.DataFrame, sort_key: int) -> List[urwid.Text]:

    return format_data(sort_data(data, sort_key))


def get_data(symbols) -> pd.DataFrame:
    r = requests.get(
        IEX_BATCH_URL, params={"symbols": ",".join(symbols), "types": "quote"}
    )
    flattened = {k: v["quote"] for k, v in r.json().items()}

    return pd.DataFrame.from_dict(flattened, orient="index").rename(
        FIELDS, axis="columns"
    )[list(FIELDS.values())]


class UserInput:
    def __init__(self) -> None:
        self.sort_key: Optional[int] = None


class DataFrameViewer(urwid.Filler):
    def __init__(self) -> None:
        body = urwid.Columns([], dividechars=3)
        super().__init__(body, "top")
        self.data = pd.DataFrame(data=[], columns=FIELDS.values())
        self.generate_columns(None)

    def generate_columns(self, sort_key) -> None:
        self.original_widget.contents = [
            (c, self.original_widget.options("pack"))
            for c in process_for_gui((self.data), sort_key)
        ]


def handle_input(fill, user_input: UserInput, key: int) -> None:

    if key in ("q", "Q"):
        raise urwid.ExitMainLoop()
    try:
        user_input.sort_key = int(key)
        fill.generate_columns(user_input.sort_key)
    except (ValueError, TypeError):
        pass


def draw_loop(queue, loop, user_input) -> Callable[[], None]:
    def fn() -> None:

        while True:
            if not queue.empty():
                loop.widget.data = queue.get()
                loop.widget.generate_columns(user_input.sort_key)
                loop.draw_screen()

    return fn


def gui(queue) -> None:

    fill = DataFrameViewer()
    user_input = UserInput()

    loop = urwid.MainLoop(
        fill=urwid.Filler(columns, "top"),
        palette=[("bold", "light red,bold", "default")],
        unhandled_input=partial(handle_input, fill, user_input),
    )

    Thread(target=draw_loop(queue, loop, user_input), daemon=True).start()
    loop.run()


def update_loop(symbols: List[str], queue: Queue) -> Callable[[], None]:
    def fn() -> None:
        while True:
            queue.put(get_data(symbols))
            sleep(5)

    return fn


def stocks_monitor(symbols: List[str]) -> None:

    queue: Queue = Queue(1)
    Thread(target=update_loop(symbols, queue), daemon=True).start()
    gui(queue)


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
