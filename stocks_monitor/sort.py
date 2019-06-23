"""
Sorting logic for stocks_monitor UI.
"""
from queue import Queue
from typing import Generator, Iterable, Tuple

import pandas as pd


def sort_data(queue: Queue) -> Iterable[pd.DataFrame]:

    dataframe, sort_key = None, 0
    while not isinstance(dataframe, pd.DataFrame):
        dataframe = queue.get()

    sort_direction = new_sort_direction(sort_key, dataframe.dtypes[sort_key])
    direction = next(sort_direction)
    yield sort_and_update_names(dataframe, direction, sort_key)

    while True:
        arrival = queue.get()
        if isinstance(arrival, pd.DataFrame):
            dataframe = arrival
        else:
            sort_key, dtype = arrival, dataframe.dtypes[arrival]
            direction = sort_direction.send((sort_key, dtype))
        yield sort_and_update_names(dataframe, direction, sort_key)


def new_sort_direction(
    sort_key, dtype
) -> Generator[bool, Tuple[int, str], None]:

    previous_key, direction = None, default_sort_direction(dtype)
    while True:
        (key, dtype) = yield direction
        if previous_key != key:
            previous_key, direction = key, default_sort_direction(dtype)
        else:
            direction = not direction


def sort_and_update_names(
    df: pd.DataFrame, direction: bool, sort_key: int
) -> pd.DataFrame:
    name = df.columns[sort_key]

    return df.sort_values(by=name, ascending=direction).rename(
        mapper={name: add_arrow(name, direction)}, axis="columns"
    )


def default_sort_direction(dtype: str) -> bool:
    return True if dtype == "object" else False


def add_arrow(name: str, direction: bool) -> str:

    if direction is True:
        return name + " ⬇"
    return name + " ⬆"
