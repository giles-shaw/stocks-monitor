from typing import Dict, List

import numpy as np
import pandas as pd
import requests
from time import sleep

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"


def data_feed(
    symbols: List[str], fields: Dict[str, str], wait: float = 1
) -> pd.DataFrame:

    while True:
        response = requests.get(
            IEX_BATCH_URL,
            params={"symbols": ",".join(symbols), "types": "quote"},
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
    symbols: List[str], fields: Dict[str, str], wait: float = 1
) -> pd.DataFrame:

    df = next(data_feed(symbols, fields))
    while True:
        numeric_cols = [c for c in df if df[c].dtype in (float, int)]
        for col in numeric_cols:
            df.loc[:, col] += np.random.normal(
                0, df.loc[:, col].std() / 10, (len(df),)
            )

        yield df
        sleep(wait)
