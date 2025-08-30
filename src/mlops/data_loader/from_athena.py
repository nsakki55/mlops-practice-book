import logging
from datetime import datetime

import awswrangler as wr
import pandas as pd

from mlops.const import GLUE_DATABASE

logger = logging.getLogger(__name__)
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def compose_sql(
    table: str,
    from_datetime: datetime | None = None,
    to_datetime: datetime | None = None,
    additional_where_clause: str | None = None,
) -> str:
    logger.info(f"Start compose sql. {table=}, {from_datetime=}, {to_datetime=}.")
    sql = f"SELECT * FROM {table}"

    # データ取得の開始時刻と終了時刻からwhere句を作成
    where_clause = []
    if from_datetime is not None:
        where_clause += [f"logged_at >= '{from_datetime.strftime(DATETIME_FORMAT)}'"]
    if to_datetime is not None:
        where_clause += [f"logged_at <= '{to_datetime.strftime(DATETIME_FORMAT)}'"]
    # 指定したwhere句を追加
    if additional_where_clause:
        where_clause += [additional_where_clause]
    if where_clause:
        sql += " WHERE " + " AND ".join(where_clause)

    logger.info(f"Finish compose sql. {sql=}")

    return sql


def extract_dataframe_from_athena(sql: str, database: str = GLUE_DATABASE) -> pd.DataFrame:
    logger.info(f"Start extracting data from Athena. {sql=}, {database=}.")
    df = wr.athena.read_sql_query(sql, database=database, ctas_approach=False)
    assert len(df) != 0

    logger.info(f"Finish extracting data from Athena. {len(df)=}.")

    return df
