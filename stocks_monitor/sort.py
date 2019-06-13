from queue import Queue
from collections import namedtuple
from typing import Tuple, cast

import pandas as pd


def sort(queue: Queue) -> pd.DataFrame:

    data, s_key = None, 0
    while data is None:
        arrival = queue.get()
        if not isinstance(arrival, SortKey):
            acting_on_input = False
            data = sort_df(arrival, s_key, False, (SortStatus(False, False),))
            yield data
    while True:
        sort_signature = df_sort_status(data)
        arrival = queue.get()
        if isinstance(arrival, SortKey):
            s_key = arrival.sort_key
            acting_on_input = True
        else:
            data = arrival
            acting_on_input = False
        data = sort_df(data, s_key, acting_on_input, sort_signature)
        yield data


class SortKey:
    def __init__(self, sort_key: int = 0) -> None:
        self.sort_key = sort_key


SortStatus = namedtuple("SortStatus", ["ascending", "descending"])


def sort_df(
    df: pd.DataFrame,
    sort_key: int,
    acting_on_input: bool,
    previous_sort_signature: Tuple[SortStatus],
) -> pd.DataFrame:
    return df.sort_values(
        by=df.columns[sort_key],
        ascending=sort_direction(
            series=df.iloc[:, sort_key],
            acting_on_input=acting_on_input,
            sort_status=previous_sort_signature[sort_key],
        ),
    )


def df_sort_status(df: pd.DataFrame) -> Tuple[SortStatus]:
    return cast(
        Tuple[SortStatus], tuple(column_sort_status(df[c]) for c in df)
    )


def sort_direction(
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


def column_sort_status(series: pd.Series) -> SortStatus:

    consecutive_pairs = list(zip(series[:-1], series[1:]))

    ascending = all(a <= b for a, b in consecutive_pairs)
    descending = all(a >= b for a, b in consecutive_pairs)

    return SortStatus(ascending, descending)
