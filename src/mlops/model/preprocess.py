import logging

import pandas as pd
from sklearn.model_selection import train_test_split

from .schema import Schema

logger = logging.getLogger(__name__)


def apply_preprocess(
    df_impression_log: pd.DataFrame,
    df_view_log: pd.DataFrame,
    df_item: pd.DataFrame,
    lookback_days: int = 7,
) -> pd.DataFrame:
    logger.info(f"Start common preprocess {len(df_impression_log)=}, {len(df_view_log)=}, {len(df_item)=}, {lookback_days=}")

    df_impression_time_feature = _get_impression_time_feature(df_impression_log)
    df_impression_history_feature = _get_impression_history_feature(df_impression_log, lookback_days=lookback_days)
    df_view_history_feature = _get_view_history_feature(df_impression_log, df_view_log, lookback_days=lookback_days)

    df = df_impression_log.merge(df_impression_time_feature, how="left", on="impression_id")
    df = df.merge(df_impression_history_feature, how="left", on="impression_id")
    df = df.merge(df_view_history_feature, how="left", on="impression_id")
    df = df.merge(df_item, how="left", on="item_id")

    logger.info(f"Finished common preprocess {len(df)=}, {df.head()}")
    return df


def get_impression_feature(
    df_impression_log: pd.DataFrame,
    df_view_log: pd.DataFrame,
    df_item: pd.DataFrame,
    lookback_days: int = 7,
) -> pd.DataFrame:
    logger.info(
        f"Start get impression feature {len(df_impression_log)=}, {len(df_view_log)=}, {len(df_item)=}, {lookback_days=}"
    )

    df_impression_history_feature = _get_impression_history_feature(df_impression_log, lookback_days=lookback_days)
    df_view_history_feature = _get_view_history_feature(df_impression_log, df_view_log, lookback_days=lookback_days)

    df = df_impression_log.merge(df_impression_history_feature, how="left", on="impression_id")
    df = df.merge(df_view_history_feature, how="left", on="impression_id")
    df = pd.merge(df, df_item, on="item_id", how="left")

    logger.info(f"Finished impression feature {len(df)=}, {df.head()}")

    return df


def apply_schema(
    df: pd.DataFrame,
    schemas: list[Schema],
) -> pd.DataFrame:
    logger.info(f"Start apply schema {len(df)=}, {len(schemas)=}")
    for schema in schemas:
        df[schema.name] = df[schema.name].fillna(schema.null_value)
        df[schema.name] = df[schema.name].astype(schema.dtype)
    return df


def apply_train_test_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
    valid_size: float = 0.1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    logger.info(f"Start get train dataset. {len(df)=}, {test_size=}, {valid_size=}")

    # Sort by impression time to split data based on the impression time
    df = df.sort_values(by="logged_at")
    # TODO: valid, testを割合ではなく、日にちで分割する。今だと学習データ期間が変わると、valid, testデータが変わってしまう。

    df_train, df_test = train_test_split(df, test_size=test_size, random_state=42, shuffle=False)
    df_train, df_valid = train_test_split(df_train, test_size=valid_size, random_state=42, shuffle=False)

    return df_train, df_valid, df_test


def _get_impression_history_feature(
    df_impression_log: pd.DataFrame,
    lookback_days: int = 7,
) -> pd.DataFrame:
    df_impression_history = df_impression_log.merge(df_impression_log, how="left", on="user_id", suffixes=("", "_previous"))

    df_impression_history["days_between_impressions"] = (
        df_impression_history["logged_at"] - df_impression_history["logged_at_previous"]
    ).dt.days

    df_impression_history = df_impression_history.query(
        f"(logged_at_previous < logged_at) and (days_between_impressions <= {lookback_days})"
    )

    df_impression_history_feature = (
        df_impression_history.groupby("impression_id")["impression_id_previous"]
        .count()
        .reset_index(name="previous_impression_count")
    )

    df_impression_history_feature["previous_impression_count"] = df_impression_history_feature[
        "previous_impression_count"
    ].astype(pd.Int64Dtype())
    return df_impression_history_feature


def _get_view_history_feature(
    df_impression_log: pd.DataFrame,
    df_view_log: pd.DataFrame,
    lookback_days: int = 7,
) -> pd.DataFrame:
    df_view_log_drop_duplicated = df_view_log.drop_duplicates(subset=["user_id", "logged_at"], keep="last")
    df_view_history = df_impression_log.merge(
        df_view_log_drop_duplicated,
        how="left",
        on="user_id",
        suffixes=("_impression", "_view"),
    )

    df_view_history["days_between_impression_and_session"] = (
        df_view_history["logged_at_impression"] - df_view_history["logged_at_view"]
    ).dt.days

    df_view_history = df_view_history.query(
        f"(logged_at_view < logged_at_impression) and (days_between_impression_and_session <= {lookback_days})"
    )
    df_view_history_features = (
        df_view_history.groupby(
            "impression_id",
        )
        .agg(
            previous_view_count=("logged_at_view", "count"),
            item_id=("item_id", "last"),
            device_type=("device_type", "last"),
        )
        .reset_index()
    )

    df_view_history_features["previous_view_count"] = df_view_history_features["previous_view_count"].astype(pd.Int64Dtype())

    return df_view_history_features


def _get_impression_time_feature(
    df_impression_log: pd.DataFrame,
) -> pd.DataFrame:
    df_impression_time_feature = pd.DataFrame(
        {
            "impression_id": df_impression_log["impression_id"],
            "impression_hour": df_impression_log["logged_at"].dt.hour,
            "impression_day": df_impression_log["logged_at"].dt.day,
            "impression_weekday": df_impression_log["logged_at"].dt.weekday,
        }
    )
    return df_impression_time_feature


def add_impression_time_feature(
    df: pd.DataFrame,
    impression_time_column: str,
) -> pd.DataFrame:
    df[impression_time_column] = pd.to_datetime(df[impression_time_column])
    df["impression_hour"] = df[impression_time_column].dt.hour
    df["impression_day"] = df[impression_time_column].dt.day
    df["impression_weekday"] = df[impression_time_column].dt.weekday
    return df
