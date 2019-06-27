"""
Helper formatting functions to convert pd.DataFrame values to displayable text
characters.
"""
from collections import OrderedDict
from typing import Any, Dict, Union, List, Tuple, Optional

import pandas as pd
import urwid


def format_column_names(
    column_names: Tuple[str, ...], sort_key: int, direction: Optional[bool]
) -> Dict[str, str]:

    if direction is not None:
        labelled_names = [
            add_arrow(name, direction, preceeding=(sort_key == 0))
            if ix == sort_key
            else name
            for ix, name in enumerate(column_names)
        ]
    else:
        labelled_names = list(column_names)

    formatted_names = [
        format_name(name, left_align=(ix == 0))
        for ix, name in enumerate(labelled_names)
    ]
    return dict(zip(column_names, formatted_names))


def add_arrow(name: str, direction: bool, preceeding: bool = False) -> str:
    if preceeding:
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


def format_dataframe(df: pd.DataFrame) -> List[urwid.Text]:

    df_str = df.applymap(format_entry)
    text_cols = [[("bold", c)] + df_str[c].to_list() for c in df_str]

    return [
        urwid.Text(tc, align="left" if ix == 0 else "right")
        for ix, tc in enumerate(text_cols)
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
