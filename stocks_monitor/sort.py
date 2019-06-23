"""
Sorting logic for stocks_monitor UI.
"""
from queue import Queue
from typing import Generator, Iterable, Tuple

import pandas as pd

from stocks_monitor.format import add_arrow


def sort_data(queue: Queue) -> Iterable[pd.DataFrame]:

    dataframe, sort_key = None, 0
    while not isinstance(dataframe, pd.DataFrame):
        dataframe = queue.get()

    new_sort_direction = sort_direction(sort_key, dataframe.dtypes[sort_key])
    direction = next(new_sort_direction)
    yield processed_dataframe(dataframe, direction, sort_key)

    while True:
        arrival = queue.get()
        if isinstance(arrival, pd.DataFrame):
            dataframe = arrival
        else:
            sort_key, dtype = arrival, dataframe.dtypes[arrival]
            direction = new_sort_direction.send((sort_key, dtype))
        yield processed_dataframe(dataframe, direction, sort_key)


def sort_direction(sort_key, dtype) -> Generator[bool, Tuple[int, str], None]:

    previous_key, direction = sort_key, default_sort_direction(dtype)
    while True:
        (key, dtype) = yield direction
        if previous_key != key:
            previous_key, direction = key, default_sort_direction(dtype)
        else:
            direction = not direction


def processed_dataframe(
    df: pd.DataFrame, direction: bool, sort_key: int
) -> pd.DataFrame:
    name = df.columns[sort_key]

    return df.sort_values(by=name, ascending=direction).rename(
        mapper={name: add_arrow(name, direction)}, axis="columns"
    )


def default_sort_direction(dtype: str) -> bool:
    return True if dtype == "object" else False
