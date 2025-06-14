from datetime import datetime, timedelta

import pandas as pd
from pandas.testing import assert_frame_equal

from mlops.model import (
    Schema,
    add_impression_time_feature,
    apply_preprocess,
    apply_schema,
    apply_train_test_split,
    get_impression_feature,
)


def create_test_data():
    impression_log_data = {
        "impression_id": [1, 2, 3, 4, 5],
        "user_id": [101, 102, 101, 103, 102],
        "logged_at": [
            datetime(2023, 1, 1, 10, 0),
            datetime(2023, 1, 2, 11, 0),
            datetime(2023, 1, 3, 12, 0),
            datetime(2023, 1, 4, 13, 0),
            datetime(2023, 1, 5, 14, 0),
        ],
    }
    df_impression_log = pd.DataFrame(impression_log_data)

    view_log_data = {
        "view_id": [1001, 1002, 1003, 1004],
        "user_id": [101, 102, 101, 103],
        "item_id": [201, 202, 206, 207],
        "device_type": ["mobile", "desktop", "mobile", "tablet"],
        "logged_at": [
            datetime(2022, 12, 30, 9, 0),
            datetime(2022, 12, 31, 10, 0),
            datetime(2023, 1, 2, 11, 0),
            datetime(2023, 1, 3, 12, 0),
        ],
    }
    df_view_log = pd.DataFrame(view_log_data)

    item_data = {
        "item_id": [201, 202, 203, 204, 205, 206, 207],
        "category": ["A", "B", "A", "C", "B", "A", "C"],
        "price": [100, 200, 150, 300, 250, 120, 280],
    }
    df_item = pd.DataFrame(item_data)

    return df_impression_log, df_view_log, df_item


def test_apply_preprocess():
    df_impression_log, df_view_log, df_item = create_test_data()
    expected_date = {
        "impression_id": [1, 2, 3, 4, 5],
        "user_id": [101, 102, 101, 103, 102],
        "logged_at": pd.to_datetime(
            [
                "2023-01-01T10:00:00.000000000",
                "2023-01-02T11:00:00.000000000",
                "2023-01-03T12:00:00.000000000",
                "2023-01-04T13:00:00.000000000",
                "2023-01-05T14:00:00.000000000",
            ]
        ),
        "impression_hour": [10, 11, 12, 13, 14],
        "impression_day": [1, 2, 3, 4, 5],
        "impression_weekday": [6, 0, 1, 2, 3],
        "previous_impression_count": [None, None, 1, None, 1],
        "previous_view_count": [1, 1, 2, 1, 1],
        "item_id": [201, 202, 206, 207, 202],
        "device_type": ["mobile", "desktop", "mobile", "tablet", "desktop"],
        "category": ["A", "B", "A", "C", "B"],
        "price": [100, 200, 120, 280, 200],
    }
    df_expected = pd.DataFrame(expected_date)

    df_actual = apply_preprocess(df_impression_log, df_view_log, df_item, lookback_days=7)

    assert_frame_equal(df_expected, df_actual, check_dtype=False)


def test_get_impression_feature():
    df_impression_log, df_view_log, df_item = create_test_data()
    expected_date = {
        "impression_id": [1, 2, 3, 4, 5],
        "user_id": [101, 102, 101, 103, 102],
        "logged_at": pd.to_datetime(
            [
                "2023-01-01T10:00:00.000000000",
                "2023-01-02T11:00:00.000000000",
                "2023-01-03T12:00:00.000000000",
                "2023-01-04T13:00:00.000000000",
                "2023-01-05T14:00:00.000000000",
            ]
        ),
        "previous_impression_count": [None, None, 1, None, 1],
        "previous_view_count": [1, 1, 2, 1, 1],
        "item_id": [201, 202, 206, 207, 202],
        "device_type": ["mobile", "desktop", "mobile", "tablet", "desktop"],
        "category": ["A", "B", "A", "C", "B"],
        "price": [100, 200, 120, 280, 200],
    }
    df_expected = pd.DataFrame(expected_date)

    df_actual = get_impression_feature(df_impression_log, df_view_log, df_item, lookback_days=7)

    assert_frame_equal(df_expected, df_actual, check_dtype=False)


def test_apply_schema():
    test_data = {"int_col": [1, 2, None, 4, 5], "float_col": [1.1, 2.2, None, 4.4, 5.5], "str_col": ["a", "b", None, "d", "e"]}
    df_test = pd.DataFrame(test_data)
    schemas = [
        Schema(name="int_col", dtype="int64", null_value=0),
        Schema(name="float_col", dtype="float", null_value=0.0),
        Schema(name="str_col", dtype="str", null_value="missing"),
    ]

    result = apply_schema(df_test, schemas)

    assert result["int_col"].iloc[2] == 0
    assert result["float_col"].iloc[2] == 0.0
    assert result["str_col"].iloc[2] == "missing"
    assert result["int_col"].dtype == "int64"
    assert result["float_col"].dtype == "float64"
    assert result["str_col"].dtype == "object"


def test_apply_train_test_split():
    test_data = {"feature": list(range(100)), "logged_at": [datetime(2023, 1, 1) + timedelta(hours=i) for i in range(100)]}
    df_test = pd.DataFrame(test_data)

    df_train, df_valid, df_test = apply_train_test_split(df_test, test_size=0.2, valid_size=0.1)

    assert len(df_train) == 72
    assert len(df_valid) == 8
    assert len(df_test) == 20
    assert df_train["logged_at"].max() < df_valid["logged_at"].min()
    assert df_valid["logged_at"].max() < df_test["logged_at"].min()


def test_add_impression_time_feature():
    test_data = {
        "impression_id": [1, 2, 3],
        "timestamp": pd.to_datetime(
            ["2023-01-01 10:00:00", "2023-01-02 11:00:00", "2023-01-03 12:00:00"]
        ),
    }
    df_test = pd.DataFrame(test_data)

    df_actual = add_impression_time_feature(df_test, "timestamp")

    assert df_actual["impression_hour"].tolist() == [10, 11, 12]
    assert df_actual["impression_day"].tolist() == [1, 2, 3]
    assert df_actual["impression_weekday"].tolist() == [6, 0, 1]
