"""
Main control flow for stocks_monitor.
"""
from queue import Queue
from threading import Thread
from typing import Callable, Iterable

import pandas as pd
import urwid

from stocks_monitor.dataframe_widget import DataFrameWidget, SortKey
from stocks_monitor.sort import sort_direction, SortStatus, df_sort_status


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

    Thread(target=update_loop(queue, loop), daemon=True).start()
    loop.run()


def update_loop(queue: Queue, loop: urwid.MainLoop) -> Callable[[], None]:
    def fn() -> None:
        s_key = 0
        arrival = queue.get()
        if not isinstance(arrival, SortKey):
            acting_on_input = False
            data = arrival.sort_values(
                by=arrival.columns[s_key],
                ascending=sort_direction(
                    series=arrival.iloc[:, s_key],
                    acting_on_input=acting_on_input,
                    sort_status=SortStatus(False, False),
                ),
            )
            sort_signature = df_sort_status(data)
        while True:
            arrival = queue.get()
            if isinstance(arrival, SortKey):
                s_key = arrival.sort_key
                acting_on_input = True
            else:
                data = arrival
                acting_on_input = False
            data = data.sort_values(
                by=data.columns[s_key],
                ascending=sort_direction(
                    series=data.iloc[:, s_key],
                    acting_on_input=acting_on_input,
                    sort_status=sort_signature[s_key],
                ),
            )
            sort_signature = df_sort_status(data)
            loop.widget.update_columns(data)
            loop.draw_screen()

    return fn
