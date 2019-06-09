from typing import Dict, List

import numpy as np
import pandas as pd
import requests

IEX_BATCH_URL = "https://api.iextrading.com/1.0/stock/market/batch"


def get_data(symbols: List[str], fields: Dict[str, str]) -> pd.DataFrame:

    response = requests.get(
        IEX_BATCH_URL, params={"symbols": ",".join(symbols), "types": "quote"}
    )
    response.raise_for_status()

    flattened = {k: v["quote"] for k, v in response.json().items()}
    if not set(symbols).issubset(set(flattened)):
        raise KeyError(
            "Unable to retrieve stock data for: "
            f"{set(symbols)-set(flattened)}"
        )

    return pd.DataFrame.from_dict(flattened, orient="index")[
        list(fields)
    ].rename(fields, axis="columns")


def get_fake_data(symbols: List[str], fields: Dict[str, str]) -> pd.DataFrame:

    df = get_data(symbols, fields)
    numeric_cols = [c for c in df if df[c].dtype in (float, int)]
    for col in numeric_cols:
        df.loc[:, col] += np.random.normal(
            0, df.loc[:, col].std() / 10, (len(df),)
        )

    return df
