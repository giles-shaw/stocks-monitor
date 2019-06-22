"""
Sorting logic for stocks_monitor UI.
"""
from enum import Enum
from queue import Queue
from typing import Iterable

import pandas as pd


def sort_data(queue: Queue) -> Iterable[pd.DataFrame]:

    arrival, sort_key = None, 0
    while not isinstance(arrival, pd.DataFrame):
        arrival = queue.get()

    direction = sort_direction(
        arrival.iloc[:, sort_key], False, SortStatus.unsorted
    )
    sorted_data = arrival.sort_values(
        by=arrival.columns[sort_key], ascending=direction
    )
    yield sorted_data

    while True:
        arrival = queue.get()
        if isinstance(arrival, pd.DataFrame):
            sorted_data = arrival.sort_values(
                by=arrival.columns[sort_key], ascending=direction
            )
        else:
            sort_key = arrival
            sort_status = column_sort_status(sorted_data.iloc[:, sort_key])
            direction = sort_direction(
                sorted_data.iloc[:, sort_key], True, sort_status
            )
            sorted_data = sorted_data.sort_values(
                by=sorted_data.columns[sort_key], ascending=direction
            )
        yield sorted_data


SortStatus = Enum("SortStatus", ["unsorted", "ascending", "descending"])


def sort_direction(
    series: pd.Series, acting_on_input: bool, sort_status: SortStatus
) -> bool:

    if sort_status == SortStatus.unsorted:
        return True if series.dtype == "object" else False
    else:
        # If the column is already sorted and the user has acted, reverse the
        # sorting direction. Otherwise, maintain it.
        if acting_on_input:
            if sort_status == SortStatus.ascending:
                return False
            return True
        else:
            if sort_status == SortStatus.ascending:
                return True
            return False


def column_sort_status(series: pd.Series) -> SortStatus:

    consecutive_pairs = list(zip(series[:-1], series[1:]))

    if all(a <= b for a, b in consecutive_pairs):
        return SortStatus.ascending
    elif all(a >= b for a, b in consecutive_pairs):
        return SortStatus.descending
    else:
        return SortStatus.unsorted
