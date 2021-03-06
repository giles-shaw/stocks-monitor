"""
Wrapper for urwid.Filler designed to display information from a DataFrame
and pass on user input to a queue for processing.
"""
from queue import Queue
from typing import Any, Callable, Optional

import pandas as pd
import urwid

from stocks_monitor.format import format_dataframe


class DataFrameWidget(urwid.Filler):
    def __init__(self, data: Optional[pd.DataFrame] = None) -> None:
        original_widget = urwid.Columns([], dividechars=3)
        super().__init__(original_widget, "top")
        if data is None:
            data = pd.DataFrame()
        self.update_columns(data)

    def update_columns(self, data: pd.DataFrame) -> None:

        self.original_widget.contents = [
            (c, self.original_widget.options("pack"))
            for c in format_dataframe(data)
        ]

    def handle_input(self, queue: Queue) -> Callable[[Any], bool]:
        def fn(key: Any) -> bool:
            if key in ("q", "Q"):
                raise urwid.ExitMainLoop()
            # Ensure input is a valid sort key.
            try:
                assert (
                    int(key) - 1 in range(len(self.original_widget.contents))
                    or int(key) == 0
                )
            except (ValueError, TypeError):
                return False
            except AssertionError:
                return False

            if int(key) == 0:
                queue.put(None)
            else:
                queue.put(int(key) - 1)
            return True

        return fn
