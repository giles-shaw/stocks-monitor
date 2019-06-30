"""
Generators to query IEX Cloud API for data.
"""
from time import sleep
from typing import Dict, Iterator, List

import numpy as np
import pandas as pd
import requests

IEX_BATCH_URL = "https://cloud.iexapis.com/stable/stock/market/batch"


def data_feed(
    symbols: List[str],
    fields: Dict[str, str],
    token: str,
    query_wait_time: float = 5,
) -> Iterator[pd.DataFrame]:

    with requests.Session() as s:
        while True:
            try:
                response = s.get(
                    IEX_BATCH_URL,
                    params={
                        "symbols": ",".join(symbols),
                        "types": "quote",
                        "token": token,
                    },
                )
                response.raise_for_status()

                flattened = {k: v["quote"] for k, v in response.json().items()}
                if not set(symbols).issubset(set(flattened)):
                    raise KeyError(
                        "Unable to retrieve stock data for: "
                        f"{set(symbols)-set(flattened)}"
                    )

                yield pd.DataFrame.from_dict(flattened, orient="index")[
                    list(fields)
                ].rename(fields, axis="columns").loc[symbols]
            except requests.ConnectionError:
                yield pd.DataFrame(data=[], columns=["Connection lost!"])
            sleep(query_wait_time)


def fake_data_feed(
    symbols: List[str],
    fields: Dict[str, str],
    token: str,
    query_wait_time: float = 5,
) -> Iterator[pd.DataFrame]:

    df = next(data_feed(symbols, fields, token))
    while True:
        numeric_cols = [c for c in df if df[c].dtype in (float, int)]
        for col in numeric_cols:
            df.loc[:, col] *= np.random.lognormal(0, 0.05, (len(df),))

        yield df
        sleep(query_wait_time)
