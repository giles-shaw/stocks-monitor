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

from stocks_monitor.dataframe_widget import DataFrameWidget, SortKey

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"


def get_data(symbols: List[str], fields: Dict[str, str]) -> pd.DataFrame:

    response = requests.get(
        IEX_BATCH_URL, params={"symbols": ",".join(symbols), "types": "quote"}
    )
    response.raise_for_status()

    flattened = {k: v["quote"] for k, v in response.json().items()}
    if not set(symbols).issubset(set(flattened)):
        raise KeyError(
            "Unable to retrieve stock data for: "
            f"{set(symbols)-set(flattened)}"
        )

    return pd.DataFrame.from_dict(flattened, orient="index")[
        list(fields)
    ].rename(fields, axis="columns")


def update_loop(
    symbols: List[str], fields: Dict[str, str], queue: Queue
) -> Callable[[], None]:
    def fn() -> None:

        while True:
            queue.put(get_data(symbols, fields))
            sleep(5)

    return fn


def draw_loop(
    queue: Queue, loop: urwid.MainLoop, sort_key: SortKey
) -> Callable[[], None]:
    def fn() -> None:

        while True:
            if not queue.empty():
                loop.widget.data = queue.get()
                loop.widget.sort_columns(
                    sort_key=sort_key.sort_key, acting_on_input=False
                )
                loop.draw_screen()
            sleep(0.1)

    return fn


def gui(queue: Queue) -> None:

    df_widget = DataFrameWidget(
        pd.DataFrame(data=[], columns="Fetching data...".split())
    )
    sort_key = SortKey()

    loop = urwid.MainLoop(
        widget=df_widget,
        palette=[("bold", "light red,bold", "default")],
        unhandled_input=df_widget.handle_input(sort_key),
    )

    Thread(target=draw_loop(queue, loop, sort_key), daemon=True).start()
    loop.run()


def stocks_monitor(symbols: List[str], fields: Dict[str, str]) -> None:

    queue: Queue = Queue(1)
    Thread(target=update_loop(symbols, fields, queue), daemon=True).start()
    gui(queue)
