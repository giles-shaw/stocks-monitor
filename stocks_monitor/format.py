from collections import OrderedDict
from typing import Any, Union, List

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
