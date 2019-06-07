"""
View a pd.DataFrame whose values are numbers or strings using an urwid widget
with the ability to sort rows according to user input.
"""
from collections import OrderedDict
from typing import Any, Callable, List, Optional, Union

import pandas as pd
import urwid


def format_entry(e: Any) -> str:

    if isinstance(e, int) or isinstance(e, float):
        return format_number(e)
    else:
        return "\n" + str(e)


def format_number(e: Union[int, float]) -> str:
    def fmt(e, thresh):
        return "\n" + f"{(e /thresh):0.2f}"

    dct = OrderedDict(
        [(10 ** 12, "T"), (10 ** 9, "B"), (10 ** 6, "M"), (1, "")]
    )
    for thresh, abrv in dct.items():
        if abs(e) > thresh:
            return fmt(e, thresh) + abrv
    if abs(e) > 0:
        return fmt(e, 1)
    raise ValueError


def format_df(df: pd.DataFrame) -> List[urwid.Text]:

    df_str = df.applymap(format_entry)
    text_cols = [[("bold", c)] + df_str[c].to_list() for c in df_str]

    return [urwid.Text(text_cols[0], align="left")] + [
        urwid.Text(tc, align="right") for tc in text_cols[1:]
    ]


def sort_df(df: pd.DataFrame, sort_key: Optional[int] = None) -> pd.DataFrame:

    if sort_key:
        try:
            field = list(df)[sort_key - 1]
            return df.sort_values(
                by=field,
                ascending=(True if df[field].dtype == "object" else False),
            )
        except IndexError:
            pass

    return df


class UserInput:
    def __init__(self) -> None:
        self.sort_key: Optional[int] = None


class DataFrameWidget(urwid.Filler):
    def __init__(self, df: pd.DataFrame = pd.DataFrame([])) -> None:
        original_widget = urwid.Columns([], dividechars=3)
        super().__init__(original_widget, "top")
        self.data = df
        self.refresh_columns()

    def refresh_columns(self, sort_key: Optional[int] = None) -> None:
        self.original_widget.contents = [
            (c, self.original_widget.options("pack"))
            for c in format_df(sort_df(self.data, sort_key))
        ]

    def sort_on_input(self, user_input: UserInput) -> Callable[[Any], bool]:
        def fn(key: Any) -> bool:
            if key in ("q", "Q"):
                raise urwid.ExitMainLoop()
            try:
                user_input.sort_key = int(key)
                self.refresh_columns(user_input.sort_key)
                return True
            except (ValueError, TypeError):
                return False

        return fn
