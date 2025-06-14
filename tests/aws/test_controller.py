import os

import boto3
import pytest
from moto import mock_aws

from mlops.aws import OnlineFeatureStoreDynamoDB, get_latest_model_version


@pytest.fixture(autouse=True)
def aws_credentials():
    os.environ["AWS_DEFAULT_REGION"] = "ap-northeast-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    yield


@mock_aws
def test_get_latest_model_version():
    client = boto3.client("dynamodb", region_name="ap-northeast-1")
    table_name = "test_model_registry"
    client.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "model", "KeyType": "HASH"}, {"AttributeName": "version", "KeyType": "RANGE"}],
        AttributeDefinitions=[
            {"AttributeName": "model", "AttributeType": "S"},
            {"AttributeName": "version", "AttributeType": "S"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    client.put_item(TableName=table_name, Item={"model": {"S": "test_model"}, "version": {"S": "1.0.0"}})
    client.put_item(TableName=table_name, Item={"model": {"S": "test_model"}, "version": {"S": "1.1.0"}})
    client.put_item(TableName=table_name, Item={"model": {"S": "test_model"}, "version": {"S": "2.0.0"}})
    client.put_item(TableName=table_name, Item={"model": {"S": "another_model"}, "version": {"S": "1.0.0"}})

    latest_version = get_latest_model_version(table_name, "test_model")
    assert latest_version == "2.0.0"

    latest_version_none = get_latest_model_version(table_name, "non_existent_model")
    assert latest_version_none is None


@mock_aws
def test_online_feature_store_dynamodb_latest_version():
    client = boto3.client("dynamodb", region_name="ap-northeast-1")
    table_name = "test_feature_store"
    client.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}, {"AttributeName": "version", "KeyType": "RANGE"}],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "N"},
            {"AttributeName": "version", "AttributeType": "N"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    client.put_item(
        TableName=table_name,
        Item={"user_id": {"N": "123"}, "version": {"N": "1"}, "feature1": {"S": "value1"}, "feature2": {"N": "42"}},
    )
    client.put_item(
        TableName=table_name,
        Item={"user_id": {"N": "123"}, "version": {"N": "2"}, "feature1": {"S": "value2"}, "feature2": {"N": "43"}},
    )

    feature_store = OnlineFeatureStoreDynamoDB(table_name, "latest")

    features = feature_store.get_impression_feature(123)
    assert features["version"] == "2"
    assert features["feature1"] == "value2"
    assert features["feature2"] == "43"

    empty_features = feature_store.get_impression_feature(456)
    assert empty_features == {}


@mock_aws
def test_online_feature_store_dynamodb_specific_version():
    client = boto3.client("dynamodb", region_name="ap-northeast-1")
    table_name = "test_feature_store"
    client.create_table(
        TableName=table_name,
        KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}, {"AttributeName": "version", "KeyType": "RANGE"}],
        AttributeDefinitions=[
            {"AttributeName": "user_id", "AttributeType": "N"},
            {"AttributeName": "version", "AttributeType": "N"},
        ],
        ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
    )
    client.put_item(
        TableName=table_name,
        Item={"user_id": {"N": "123"}, "version": {"N": "1"}, "feature1": {"S": "value1"}, "feature2": {"N": "42"}},
    )
    client.put_item(
        TableName=table_name,
        Item={"user_id": {"N": "123"}, "version": {"N": "2"}, "feature1": {"S": "value2"}, "feature2": {"N": "43"}},
    )

    feature_store = OnlineFeatureStoreDynamoDB(table_name, 1)

    features = feature_store.get_impression_feature(123)
    assert features["version"] == "1"
    assert features["feature1"] == "value1"
    assert features["feature2"] == "42"
