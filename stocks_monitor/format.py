"""
Helper formatting functions to convert pd.DataFrame values to displayable text
characters.
"""
from collections import OrderedDict
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
import urwid


def format_column_names(
    names: Tuple[str, ...], arrow_ix: Optional[int], direction: bool = False
) -> Dict[str, str]:

    labelled_names = [
        add_arrow(name, ix, direction)
        if ix == arrow_ix
        else add_spaces(name, ix)
        for ix, name in enumerate(names)
    ]
    return dict(zip(names, labelled_names))


def add_arrow(name: str, name_ix: int, direction: bool) -> str:

    arrow = "▼" if direction else "▲"
    return (name + " " + arrow) if name_ix == 0 else (arrow + " " + name)


def add_spaces(name: str, name_ix: int) -> str:

    return (name + "  ") if name_ix == 0 else ("  " + name)


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
        [
            (10 ** 12, "T"),
            (10 ** 9, "B"),
            (10 ** 6, "M"),
            (1, ""),
            (0.1, "E-1"),
            (0.01, "E-2"),
            (0.001, "E-3"),
        ]
    )
    for thresh, abrv in dct.items():
        if abs(e) > thresh:
            return fmt(e, thresh) + abrv
    else:
        return fmt(e, 1)
