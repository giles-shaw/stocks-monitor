"""
Main control flow for stocks_monitor.
"""
from queue import Queue
from threading import Thread
from typing import Callable, Iterable

import pandas as pd
import urwid

from stocks_monitor.dataframe_widget import DataFrameWidget, SortKey


def monitor(data_feed: Iterable[pd.DataFrame]) -> None:

    queue: Queue = Queue(1)

    def update_loop() -> None:

        for data in data_feed:
            queue.put(data)

    Thread(target=update_loop, daemon=True).start()
    gui(queue)


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


def draw_loop(
    queue: Queue, loop: urwid.MainLoop, sort_key: SortKey
) -> Callable[[], None]:
    def fn() -> None:

        while True:
            loop.widget.data = queue.get()
            loop.widget.sort_columns(sort_key.sort_key, user_input=False)
            loop.draw_screen()

    return fn
