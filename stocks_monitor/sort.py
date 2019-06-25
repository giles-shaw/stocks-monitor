"""
Sorting logic for stocks_monitor UI.
"""
from numbers import Number
from queue import Queue
from typing import Generator, Iterable, Tuple

import pandas as pd

from stocks_monitor.format import add_arrow


def sort_data(queue: Queue) -> Iterable[pd.DataFrame]:

    candidate = queue.get()
    while not isinstance(candidate, pd.DataFrame):
        candidate = queue.get()
    dataframe = candidate

    arrival, new_sort_direction = 0, sort_direction()
    next(new_sort_direction)

    while True:
        if isinstance(arrival, pd.DataFrame):
            dataframe = arrival
        else:
            sort_key = arrival
            is_numeric = numeric(dataframe.iloc[:, sort_key])
            direction = new_sort_direction.send((sort_key, is_numeric))
        yield processed_dataframe(dataframe, direction, sort_key)
        arrival = queue.get()


def sort_direction() -> Generator[bool, Tuple[int, bool], None]:

    previous_key = None
    (key, is_numeric) = yield False
    while True:
        if previous_key != key:
            previous_key, direction = key, not is_numeric
        else:
            direction = not direction
        (key, is_numeric) = yield direction


def processed_dataframe(
    dataframe: pd.DataFrame, direction: bool, sort_key: int
) -> pd.DataFrame:
    name = dataframe.columns[sort_key]

    return dataframe.sort_values(by=name, ascending=direction).rename(
        mapper={name: add_arrow(name, direction)}, axis="columns"
    )


def numeric(series: pd.Series) -> bool:

    return all(isinstance(v, Number) for v in set(series.values))
