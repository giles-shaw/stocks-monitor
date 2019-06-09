"""
View a pd.DataFrame whose values are numbers or strings using an urwid widget
with the ability to sort rows according to user input.
"""
from typing import Any, Callable, List, Union

import pandas as pd
import urwid

from stocks_monitor.format import format_df
from stocks_monitor.sort import get_sort_direction, get_sort_signature, SortKey


class DataFrameWidget(urwid.Filler):
    def __init__(self, df: pd.DataFrame = pd.DataFrame([])) -> None:
        original_widget = urwid.Columns([], dividechars=3)
        super().__init__(original_widget, "top")
        self.data = df
        self.sort_signature = get_sort_signature(self.data)
        self.sort_columns(sort_key=0, acting_on_input=False)

    def get_sort_direction(self, sort_key: int, acting_on_input: bool):
        return get_sort_direction(
            self.data.iloc[:, sort_key],
            acting_on_input,
            self.sort_signature[sort_key],
        )

    def sort_columns(self, sort_key: int, acting_on_input: bool) -> None:

        sorted_df = self.data.sort_values(
            by=self.data.columns[sort_key],
            ascending=self.get_sort_direction(sort_key, acting_on_input),
        )
        self.sort_signature = get_sort_signature(sorted_df)

        self.original_widget.contents = [
            (c, self.original_widget.options("pack"))
            for c in format_df(sorted_df)
        ]

    def handle_input(self, sort_key: SortKey) -> Callable[[Any], bool]:
        def fn(key: Any) -> bool:
            if key in ("q", "Q"):
                raise urwid.ExitMainLoop()
            # Ensure that input is a valid sort key.
            try:
                assert int(key) - 1 in range(self.data.shape[1])
            except (AssertionError, ValueError, TypeError):
                return False

            sort_key.sort_key = int(key) - 1
            self.sort_columns(sort_key.sort_key, acting_on_input=True)
            return True

        return fn
