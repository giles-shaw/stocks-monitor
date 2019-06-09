"""
Main control flow for stocks_monitor.
"""
from queue import Queue
from threading import Thread
from time import sleep
from typing import Callable, Dict, List, Iterator

import pandas as pd
import urwid

from stocks_monitor.data import data_feed, fake_data_feed
from stocks_monitor.dataframe_widget import DataFrameWidget, SortKey


def update_loop(
    data_feed: Iterator[pd.DataFrame], queue: Queue
) -> Callable[[], None]:
    def fn() -> None:

        for data in data_feed:
            queue.put(data)
            sleep(1)

    return fn


def draw_loop(
    queue: Queue, loop: urwid.MainLoop, sort_key: SortKey
) -> Callable[[], None]:
    def fn() -> None:

        while True:
            if not queue.empty():
                loop.widget.data = queue.get()
                loop.widget.sort_columns(
                    sort_key.sort_key, acting_on_input=False
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


def stocks_monitor(
    symbols: List[str], fields: Dict[str, str], testing_mode: bool = False
) -> None:

    queue: Queue = Queue(1)

    _data_feed = (
        fake_data_feed(symbols, fields)
        if testing_mode
        else data_feed(symbols, fields)
    )

    Thread(target=update_loop(_data_feed, queue), daemon=True).start()
    gui(queue)
