import awswrangler as wr
import pytest

from mlops.data_validator import IMPRESSION_LOG_SCHEMA, MST_ITEM_SCHEMA, VIEW_LOG_SCHEMA
from mlops.const import ATHENA_DATABASE


@pytest.mark.integration
@pytest.mark.parametrize(
    "schema", [IMPRESSION_LOG_SCHEMA, VIEW_LOG_SCHEMA, MST_ITEM_SCHEMA], ids=["impression_log", "view_log", "mst_item"]
)
def test_schema_validation(schema):
    sql = f"SELECT * FROM {schema.name} LIMIT 10"

    df = wr.athena.read_sql_query(sql, database=ATHENA_DATABASE, ctas_approach=False)

    assert len(df) > 0, "No data retrieved"
    validated_df = schema.validate(df)
    assert len(validated_df) == len(df), "Row count changed after validation"
