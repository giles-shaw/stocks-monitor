from typing import Dict, List, Iterator

import numpy as np
import pandas as pd
import requests
from time import sleep

IEX_BATCH_URL = "https://cloud.iexapis.com/stable/stock/market/batch"


def data_feed(
    symbols: List[str],
    fields: Dict[str, str],
    token: str,
    wait: float = 1,
) -> Iterator[pd.DataFrame]:

    while True:
        response = requests.get(
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
        ].rename(fields, axis="columns")
        sleep(wait)


def fake_data_feed(
    symbols: List[str],
    fields: Dict[str, str],
    token: str,
    wait: float = 1,
) -> Iterator[pd.DataFrame]:

    df = next(data_feed(symbols, fields, token))
    while True:
        numeric_cols = [c for c in df if df[c].dtype in (float, int)]
        for col in numeric_cols:
            df.loc[:, col] += np.random.normal(
                0, abs(df.loc[:, col].mean()) / 10, (len(df),)
            )

        yield df
        sleep(wait)
