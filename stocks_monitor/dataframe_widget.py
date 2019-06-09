"""
View a pd.DataFrame whose values are numbers or strings using an urwid widget
with the ability to sort rows according to user input.
"""
from collections import namedtuple, OrderedDict
from typing import Any, Callable, Dict, List, Union

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


SortStatus = namedtuple(
    "SortStatus", ["ascending", "descending"], defaults=[False, False]
)


class SortInfo:
    def __init__(self) -> None:
        self.sort_key: int = 1
        self.acting_on_input = False
        self.sort_signature: Dict[str, SortStatus] = {}


def get_sort_status(series: pd.Series) -> SortStatus:

    consecutive_pairs = list(zip(series[:-1], series[1:]))

    ascending = all(a <= b for a, b in consecutive_pairs)
    descending = all(a >= b for a, b in consecutive_pairs)

    return SortStatus(ascending, descending)


def sort_df(df: pd.DataFrame, sort_info: SortInfo) -> pd.DataFrame:

    field = list(df)[sort_info.sort_key - 1]
    sort_status = sort_info.sort_signature.get(field, SortStatus())

    if any(sort_status):
        sort_order = sort_status.ascending
        if sort_info.acting_on_input:
            sort_order = not sort_order
    else:
        sort_order = True if df[field].dtype == "object" else False
    if sort_info.acting_on_input:
        sort_info.acting_on_input = False

    sorted_df = df.sort_values(by=field, ascending=sort_order)
    sort_info.sort_signature = {
        f: get_sort_status(sorted_df[f]) for f in list(df)
    }
    return sorted_df


class DataFrameWidget(urwid.Filler):
    def __init__(self, df: pd.DataFrame = pd.DataFrame([])) -> None:
        original_widget = urwid.Columns([], dividechars=3)
        super().__init__(original_widget, "top")
        self.data = df
        self.refresh_columns(SortInfo())

    def refresh_columns(self, sort_info: SortInfo) -> None:
        self.original_widget.contents = [
            (c, self.original_widget.options("pack"))
            for c in format_df(sort_df(self.data, sort_info))
        ]

    def sort_on_input(self, sort_info: SortInfo) -> Callable[[Any], bool]:
        def fn(key: Any) -> bool:
            if key in ("q", "Q"):
                raise urwid.ExitMainLoop()
            # Ensure that input is a valid sort key.
            try:
                assert int(key) - 1 in range(self.data.shape[1])
            except (AssertionError, ValueError, TypeError):
                return False

            sort_info.sort_key, sort_info.acting_on_input = int(key), True
            self.refresh_columns(sort_info)
            return True

        return fn
