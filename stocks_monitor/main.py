"""
Main control flow for stocks_monitor.
"""
from queue import Queue
from threading import Thread
from typing import Callable, Iterable

import pandas as pd
import urwid

from stocks_monitor.dataframe_widget import DataFrameWidget
from stocks_monitor.sort import sort


def monitor(data_feed: Iterable[pd.DataFrame]) -> None:

    queue: Queue = Queue(1)

    def feed_loop() -> None:

        for data in data_feed:
            queue.put(data)

    Thread(target=feed_loop, daemon=True).start()
    gui(queue)


def gui(queue: Queue) -> None:

    dataframe_widget = DataFrameWidget(
        pd.DataFrame(data=[], columns="Fetching data...".split())
    )

    loop = urwid.MainLoop(
        widget=dataframe_widget,
        palette=[("bold", "light red,bold", "default")],
        unhandled_input=dataframe_widget.handle_input(queue),
    )

    sorted_data = sort(queue)
    Thread(target=update_loop(sorted_data, loop), daemon=True).start()
    loop.run()


def update_loop(
    sorted_data: Iterable[pd.DataFrame], loop: urwid.MainLoop
) -> Callable[[], None]:
    def fn() -> None:

        for data in sorted_data:
            loop.widget.update_columns(data)
            loop.draw_screen()

    return fn
