from collections import namedtuple
from queue import Queue
from typing import Iterable

import pandas as pd


def sort(queue: Queue) -> Iterable[pd.DataFrame]:

    arrival, s_key = None, 0
    while not isinstance(arrival, pd.DataFrame):
        arrival = queue.get()

    direction = sort_direction(
        arrival.iloc[:, s_key], False, SortStatus(False, False)
    )
    sorted_data = arrival.sort_values(
        by=arrival.columns[s_key], ascending=direction
    )
    yield sorted_data

    while True:
        arrival = queue.get()
        if isinstance(arrival, pd.DataFrame):
            sorted_data = arrival.sort_values(
                by=arrival.columns[s_key], ascending=direction
            )
        else:
            s_key = arrival
            sort_status = column_sort_status(sorted_data.iloc[:, s_key])
            direction = sort_direction(
                sorted_data.iloc[:, s_key], True, sort_status
            )
            sorted_data = sorted_data.sort_values(
                by=sorted_data.columns[s_key], ascending=direction
            )
        yield sorted_data


SortStatus = namedtuple("SortStatus", ["ascending", "descending"])


def sort_direction(
    series: pd.Series, acting_on_input: bool, sort_status: SortStatus
) -> bool:

    if not any(sort_status):
        return True if series.dtype == "object" else False
    else:
        # If the column is already sorted and the user has acted, reverse the
        # sorting direction. Otherwise, maintain it.
        if acting_on_input:
            return not sort_status.ascending
        else:
            return sort_status.ascending


def column_sort_status(series: pd.Series) -> SortStatus:

    consecutive_pairs = list(zip(series[:-1], series[1:]))

    ascending = all(a <= b for a, b in consecutive_pairs)
    descending = all(a >= b for a, b in consecutive_pairs)

    return SortStatus(ascending, descending)
