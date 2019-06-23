"""
Sorting logic for stocks_monitor UI.
"""
from queue import Queue
from typing import Generator, Iterable, Tuple

import pandas as pd

from stocks_monitor.format import add_arrow


def sort_data(queue: Queue) -> Iterable[pd.DataFrame]:

    candidate = None
    while not isinstance(candidate, pd.DataFrame):
        candidate = queue.get()
    dataframe = candidate

    arrival, new_sort_direction = 0, sort_direction()
    next(new_sort_direction)

    while True:
        if isinstance(arrival, pd.DataFrame):
            dataframe = arrival
        else:
            sort_key, dtype = arrival, dataframe.dtypes[arrival]
            direction = new_sort_direction.send((sort_key, dtype))
        yield processed_dataframe(dataframe, direction, sort_key)
        arrival = queue.get()


def sort_direction() -> Generator[bool, Tuple[int, str], None]:

    previous_key = None
    (key, dtype) = yield False
    while True:
        if previous_key != key:
            previous_key, direction = key, default_sort_direction(dtype)
        else:
            direction = not direction
        (key, dtype) = yield direction


def processed_dataframe(
    dataframe: pd.DataFrame, direction: bool, sort_key: int
) -> pd.DataFrame:
    name = dataframe.columns[sort_key]

    return dataframe.sort_values(by=name, ascending=direction).rename(
        mapper={name: add_arrow(name, direction)}, axis="columns"
    )


def default_sort_direction(dtype: str) -> bool:
    return True if dtype == "object" else False
