"""
View a pd.DataFrame whose values are numbers or strings using an urwid widget
with the ability to sort rows according to user input.
"""
from typing import Any, Callable, List, Optional, Union

import pandas as pd
import urwid


def format_entry(e: Any) -> str:

    if isinstance(e, int) or isinstance(e, float):
        return format_number(e)
    else:
        return "\n" + str(e)


def format_number(e: Union[int, float]) -> str:
    if e > 10 ** 12:
        return "\n" + f"{e / (10 ** 12):.2f}" + "T"
    elif e > 10 ** 9:
        return "\n" + f"{e / (10 ** 9):.2f}" + "B"
    elif e > 10 ** 6:
        return "\n" + f"{e / (10 ** 6):.2f}" + "M"
    elif isinstance(e, float):
        return "\n" + f"{e:.2f}"
    elif isinstance(e, int):
        return "\n" + str(e)
    raise ValueError


def format_df(df: pd.DataFrame) -> List[urwid.Text]:

    df_str = df.applymap(format_entry)
    text_cols = [[("bold", c)] + df_str[c].tolist() for c in df_str]

    return [urwid.Text(tc) for tc in text_cols]


def sort_df(df: pd.DataFrame, sort_key: Optional[int] = None) -> pd.DataFrame:

    if sort_key:
        try:
            field = list(df)[sort_key]
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
        self.generate_columns()

    def generate_columns(self, sort_key: Optional[int] = None) -> None:
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
                self.generate_columns(user_input.sort_key)
                return True
            except (ValueError, TypeError):
                return False

        return fn
