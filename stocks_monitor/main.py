"""
Main control flow for stocks_monitor.
"""
from queue import Queue
from threading import Thread
from time import sleep
from typing import Callable, Dict, List

import pandas as pd
import requests
import urwid

from stocks_monitor.df_widget import DataFrameWidget, UserInput

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"


def get_data(symbols, fields: Dict[str, str]) -> pd.DataFrame:
    r = requests.get(
        IEX_BATCH_URL, params={"symbols": ",".join(symbols), "types": "quote"}
    )
    flattened = {k: v["quote"] for k, v in r.json().items()}

    return pd.DataFrame.from_dict(flattened, orient="index").rename(
        fields, axis="columns"
    )[list(fields.values())]


def update_loop(
    symbols: List[str], fields: Dict[str, str], queue: Queue
) -> Callable[[], None]:
    def fn() -> None:
        while True:
            queue.put(get_data(symbols, fields))
            sleep(5)

    return fn


def draw_loop(
    queue: Queue, loop: urwid.MainLoop, user_input: UserInput
) -> Callable[[], None]:
    def fn() -> None:

        while True:
            if not queue.empty():
                loop.widget.data = queue.get()
                loop.widget.generate_columns(user_input.sort_key)
                loop.draw_screen()

    return fn


def gui(queue: Queue, fields: Dict[str, str]) -> None:

    df_widget = DataFrameWidget(
        pd.DataFrame(data=[], columns="Fetching data ...".split())
    )
    user_input = UserInput()

    loop = urwid.MainLoop(
        widget=df_widget,
        palette=[("bold", "light red,bold", "default")],
        unhandled_input=df_widget.sort_on_input(user_input),
    )

    Thread(target=draw_loop(queue, loop, user_input), daemon=True).start()
    loop.run()


def stocks_monitor(symbols: List[str], fields: Dict[str, str]) -> None:

    queue: Queue = Queue(1)
    Thread(target=update_loop(symbols, fields, queue), daemon=True).start()
    gui(queue, fields)
