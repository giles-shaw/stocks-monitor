from collections import namedtuple
from typing import Tuple, cast

import pandas as pd


class SortKey:
    def __init__(self, sort_key: int = 0) -> None:
        self.sort_key = sort_key


SortStatus = namedtuple("SortStatus", ["ascending", "descending"])


def get_sort_status(series: pd.Series) -> SortStatus:

    consecutive_pairs = list(zip(series[:-1], series[1:]))

    ascending = all(a <= b for a, b in consecutive_pairs)
    descending = all(a >= b for a, b in consecutive_pairs)

    return SortStatus(ascending, descending)


def get_sort_signature(df: pd.DataFrame) -> Tuple[SortStatus]:
    return cast(Tuple[SortStatus], tuple(get_sort_status(df[c]) for c in df))


def get_sort_direction(
    series: pd.Series, acting_on_input: bool, sort_status: SortStatus
) -> bool:

    if not any(sort_status):
        return True if series.dtype == "object" else False
    else:
        # If the column is already sorted in a direction and the user has
        # acted, reverse the sorting direction. Otherwise, maintain it.
        if acting_on_input:
            return not sort_status.ascending
        else:
            return sort_status.ascending
