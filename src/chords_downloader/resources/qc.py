from datetime import timedelta
from typing import Optional

import numpy as np
import pandas as pd
from pandas import Index, Timestamp

_MAX_INFER_GAP_MINUTES = 16


def _build_empty_row(columns: Index, missing_timestamp: Timestamp, fill_empty=np.nan) -> list:
    if not isinstance(columns, Index):
        raise TypeError(f"Expected 'columns' to be <Index>, got: {type(columns)}")
    if not isinstance(missing_timestamp, Timestamp):
        raise TypeError(f"Expected 'missing_timestamp' to be <Timestamp>, got: {type(missing_timestamp)}")
    if pd.isna(missing_timestamp):
        return None
    return [missing_timestamp if col == 'Time' else fill_empty for col in columns]


def _infer_sampling_rate(df: pd.DataFrame) -> Optional[int]:
    """Return the most common transmission interval (minutes) by inspecting consecutive timestamps.

    Only considers deltas up to _MAX_INFER_GAP_MINUTES so that actual data gaps don't skew
    the result. Returns None if no such deltas exist, signalling that gap filling should be skipped.
    """
    times = df['Time'].sort_values().reset_index(drop=True)
    deltas_minutes = times.diff().dropna().dt.total_seconds() / 60
    normal = deltas_minutes[deltas_minutes <= _MAX_INFER_GAP_MINUTES]

    if normal.empty:
        return None

    rate = int(normal.round().astype(int).mode()[0])
    return max(1, rate)


def fill_gaps(df: pd.DataFrame, set_index: bool = False) -> pd.DataFrame:
    """Insert NaN rows for any missing timestamps, inferring the sampling rate from the data.

    Requires a 'Time' column (or an index named 'Time'). If no two consecutive timestamps
    are within 16 minutes of each other the sampling rate cannot be inferred and the original
    dataframe is returned unchanged.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected <pd.DataFrame>, got: {type(df)}")

    nan_cols = df.columns[df.isna().all()]
    if not nan_cols.empty:
        print(f"[WARNING]: fill_gaps() -- fully empty columns: {nan_cols.tolist()}")

    if 'Time' not in df.columns:
        df = df.reset_index()

    df['Time'] = pd.to_datetime(df['Time'])

    nat_mask = df['Time'].isna()
    nat_count = nat_mask.sum()
    if nat_count:
        print(f"[WARNING]: fill_gaps() -- dropped {nat_count} row(s) with invalid (NaT) timestamps")
    df = df[~nat_mask].copy()

    sampling_rate = _infer_sampling_rate(df)
    if sampling_rate is None:
        print("[WARNING]: fill_gaps() -- no consecutive timestamps within 16 minutes; skipping gap fill.")
        return df

    print(f"[INFO]: fill_gaps() -- inferred sampling rate: {sampling_rate} minute(s)")

    td = timedelta(minutes=sampling_rate)
    blank_rows = []

    for i in range(len(df) - 1):
        current = df['Time'].iloc[i].replace(second=0, microsecond=0)
        nxt = df['Time'].iloc[i + 1].replace(second=0, microsecond=0)
        while nxt - current > td:
            current += td
            row = _build_empty_row(df.columns, current)
            if row is not None:
                blank_rows.append(row)

    if blank_rows:
        filler = pd.DataFrame(blank_rows, columns=df.columns)
        df = pd.concat([df, filler]).sort_values('Time').reset_index(drop=True)

    if set_index:
        df.set_index('Time', inplace=True)

    return df
