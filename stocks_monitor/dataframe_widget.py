"""
View a pd.DataFrame whose values are numbers or strings using an urwid widget
with the ability to sort rows according to user input.
"""
from typing import Any, Callable

import pandas as pd
import urwid

from stocks_monitor.format import format_df
from stocks_monitor.sort import sort_direction, df_sort_status, SortKey


class DataFrameWidget(urwid.Filler):
    def __init__(self, data: pd.DataFrame = pd.DataFrame([])) -> None:
        original_widget = urwid.Columns([], dividechars=3)
        super().__init__(original_widget, "top")
        self.data = data
        self.column_sort_status = df_sort_status(self.data)
        self.sort_columns(sort_key=0, acting_on_input=False)

    def _sort_direction(self, sort_key: int, acting_on_input: bool):

        return sort_direction(
            self.data.iloc[:, sort_key],
            acting_on_input,
            self.column_sort_status[sort_key],
        )

    def sort_columns(self, sort_key: int, acting_on_input: bool) -> None:

        sorted_df = self.data.sort_values(
            by=self.data.columns[sort_key],
            ascending=self._sort_direction(sort_key, acting_on_input),
        )
        self.column_sort_status = df_sort_status(sorted_df)

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
            except (ValueError, TypeError):
                return False
            except AssertionError:
                return False

            sort_key.sort_key = int(key) - 1
            self.sort_columns(sort_key.sort_key, acting_on_input=True)
            return True

        return fn
