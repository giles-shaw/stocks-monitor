"""
Helper formatting functions to convert pd.DataFrame values to displayable text
characters.
"""
from collections import OrderedDict
from typing import Any, Union, List

import pandas as pd
import urwid


def format_df(df: pd.DataFrame) -> List[urwid.Text]:

    df_str = df.applymap(format_entry)
    text_cols = [
        [("bold", format_name(list(df_str)[0], left_align=True))]
        + df_str[list(df_str)[0]].to_list()
    ] + [
        [("bold", format_name(c))] + df_str[c].to_list()
        for c in list(df_str)[1:]
    ]

    return [urwid.Text(text_cols[0], align="left")] + [
        urwid.Text(tc, align="right") for tc in text_cols[1:]
    ]


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
    else:
        return fmt(e, 1)


def add_arrow(name: str, direction: bool, left_align: bool = False) -> str:
    if left_align:
        return add_arrow(name[::-1], direction)[::-1]
    if direction is True:
        return "▼ " + name
    return "▲ " + name


def format_name(name: str, left_align: bool = False) -> str:

    if left_align:
        return format_name(name[::-1])[::-1]

    try:
        if name[:2] == "▲ " or name[:2] == "▼ ":
            return name
        else:
            return "  " + name
    except IndexError:
        return name
