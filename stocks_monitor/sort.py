"""
Sorting logic for stocks_monitor UI.
"""
from queue import Queue
from typing import Iterable, Union

import pandas as pd


def sort_data(queue: Queue) -> Iterable[pd.DataFrame]:

    dataframe, sort_director, sort_key = None, SortDirector(), 0
    while not isinstance(dataframe, pd.DataFrame):
        dataframe = queue.get()

    direction = sort_director.new_sort_direction(
        sort_key, dataframe.iloc[:, sort_key].dtype
    )
    sort_director.update_history(sort_key, direction)
    yield sort_and_update_names(dataframe, direction, sort_key)

    while True:
        arrival = queue.get()
        if isinstance(arrival, pd.DataFrame):
            dataframe = arrival
        else:
            sort_key = arrival
            direction = sort_director.new_sort_direction(
                sort_key, dataframe.iloc[:, sort_key].dtype
            )
            sort_director.update_history(sort_key, direction)
        yield sort_and_update_names(dataframe, direction, sort_key)


class SortDirector:
    def __init__(self):
        self.previous_sort_key: int = None
        self.previous_sort_direction: Union[bool, None] = None

    def update_history(self, sort_key: int, direction: bool) -> None:
        self.previous_sort_key = sort_key
        self.previous_sort_direction = direction

    def new_sort_direction(self, sort_key, dtype) -> bool:

        if self.previous_sort_key == sort_key:
            return not self.previous_sort_direction
        else:
            return default_sort_direction(dtype)


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
