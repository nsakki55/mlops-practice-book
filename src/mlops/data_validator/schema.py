from datetime import datetime

import pandas as pd
from pandera import Check, Column, DataFrameSchema, Index

IMPRESSION_LOG_SCHEMA = DataFrameSchema(
    name="impression_log",
    columns={
        "impression_id": Column(str, unique=True),
        "logged_at": Column(datetime),
        "user_id": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "app_code": Column(int, checks=Check.greater_than_or_equal_to(0)),
        "os_version": Column(str, checks=Check.isin(["old", "latest", "intermediate"])),
        "is_4g": Column(int, checks=Check.isin([0, 1])),
        "is_click": Column(int, checks=Check.isin([0, 1])),
    },
    index=Index(int),
    strict=True,
    coerce=True,
)

VIEW_LOG_SCHEMA = DataFrameSchema(
    name="view_log",
    columns={
        "logged_at": Column(datetime),
        "device_type": Column(pd.StringDtype(), checks=Check.isin(["android", "iphone", "web"])),
        "session_id": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
        "user_id": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
        "item_id": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
    },
    index=Index(int),
    strict=True,
    coerce=True,
)

MST_ITEM_SCHEMA = DataFrameSchema(
    name="mst_item",
    columns={
        "item_id": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
        "item_price": Column(pd.Int64Dtype(), checks=Check.greater_than(0)),
        "category_1": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
        "category_2": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
        "category_3": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
        "product_type": Column(pd.Int64Dtype(), checks=Check.greater_than_or_equal_to(0)),
    },
    index=Index(int),
    strict=True,
    coerce=True,
)
