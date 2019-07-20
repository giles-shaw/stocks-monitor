"""
Sorting logic for stocks_monitor UI.
"""
from numbers import Number
from queue import Queue
from typing import Generator, Iterable, Optional, Tuple

import pandas as pd

from stocks_monitor.format import format_column_names


def sort_data(queue: Queue) -> Iterable[pd.DataFrame]:

    candidate = queue.get()
    while not isinstance(candidate, pd.DataFrame):
        candidate = queue.get()
    dataframe = candidate

    sort_key, sort_direction_generator = None, sort_direction()
    direction = next(sort_direction_generator)

    yield processed_dataframe(dataframe, sort_key, direction)

    while True:
        arrival = queue.get()
        if isinstance(arrival, pd.DataFrame):
            dataframe = arrival
        else:
            sort_key = arrival
            numeric_col = (
                numeric(dataframe.iloc[:, sort_key]) if sort_key else False
            )
            direction = sort_direction_generator.send((sort_key, numeric_col))
        try:
            yield processed_dataframe(dataframe, sort_key, direction)
        except IndexError:
            # current sort_key is not a valid column for new dataframe
            yield processed_dataframe(dataframe, sort_key=None, direction=None)


def sort_direction() -> Generator[
    Optional[bool], Tuple[Optional[int], bool], None
]:

    previous_key = None
    (key, numeric_col) = yield None
    while True:
        if key is None:
            previous_key, direction = key, None
        elif previous_key != key:
            # Sort numeric columns in descending order by default.
            previous_key, direction = key, not numeric_col
        else:
            direction = not direction
        (key, numeric_col) = yield direction


def processed_dataframe(
    dataframe: pd.DataFrame, sort_key: Optional[int], direction: Optional[bool]
) -> pd.DataFrame:

    if sort_key is None or direction is None:
        return dataframe.rename(
            mapper=format_column_names(names=tuple(dataframe), arrow_ix=None),
            axis="columns",
        )
    name = dataframe.columns[sort_key]
    return dataframe.sort_values(by=name, ascending=direction).rename(
        mapper=format_column_names(
            names=tuple(dataframe), arrow_ix=sort_key, direction=direction
        ),
        axis="columns",
    )


def numeric(series: pd.Series) -> bool:

    return all(isinstance(v, Number) for v in set(series.values))
