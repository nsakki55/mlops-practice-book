from datetime import datetime

from mlops.data_loader import compose_sql


def test_compose_sql_with_no_parameters():
    table = "test_table"
    sql = compose_sql(table)
    assert sql == "SELECT * FROM test_table"


def test_compose_sql_with_from_datetime():
    table = "test_table"
    from_datetime = datetime(2023, 1, 1, 12, 0, 0)
    sql = compose_sql(table, from_datetime=from_datetime)
    assert sql == "SELECT * FROM test_table WHERE logged_at >= '2023-01-01 12:00:00'"


def test_compose_sql_with_to_datetime():
    table = "test_table"
    to_datetime = datetime(2023, 1, 2, 12, 0, 0)
    sql = compose_sql(table, to_datetime=to_datetime)
    assert sql == "SELECT * FROM test_table WHERE logged_at <= '2023-01-02 12:00:00'"


def test_compose_sql_with_both_datetimes():
    table = "test_table"
    from_datetime = datetime(2023, 1, 1, 12, 0, 0)
    to_datetime = datetime(2023, 1, 2, 12, 0, 0)
    sql = compose_sql(table, from_datetime=from_datetime, to_datetime=to_datetime)
    assert sql == "SELECT * FROM test_table WHERE logged_at >= '2023-01-01 12:00:00' AND logged_at <= '2023-01-02 12:00:00'"


def test_compose_sql_with_additional_where_clause():
    table = "test_table"
    additional_where_clause = "column_name = 'value'"
    sql = compose_sql(table, additional_where_clause=additional_where_clause)
    assert sql == "SELECT * FROM test_table WHERE column_name = 'value'"
