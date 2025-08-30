import logging
from pathlib import Path
from typing import Any

import boto3
import numpy as np
import pandas as pd
from boto3.dynamodb.types import TypeSerializer
from tqdm import tqdm

from mlops.const import PUBLIC_SUBNET_1A, TRAIN_SECURITY_GROUP

logger = logging.getLogger(__name__)


def download_file_from_s3(s3_bucket: str, s3_key: str, file_path: str) -> None:
    logger.info(f"Start download model file: {s3_key}, file_path: {file_path}")
    s3_client = boto3.client("s3")
    s3_client.download_file(s3_bucket, s3_key, file_path)
    logger.info(f"Finished download model file: {s3_key}, file_path: {file_path}")


def upload_dir_to_s3(dir_path: Path, s3_bucket: str, key_prefix: str) -> None:
    s3_client = boto3.client("s3")
    for file_path in dir_path.rglob("*"):
        if file_path.is_file():
            s3_key = key_prefix + "/" + str(file_path.relative_to(dir_path))
            try:
                s3_client.upload_file(str(file_path), s3_bucket, s3_key)
                logger.info(f"Uploaded {file_path} to s3://{s3_bucket}/{s3_key}")
            except Exception as e:
                logger.info(f"Failed to upload {file_path}. Error: {e}")


def upload_file_to_s3(
    s3_bucket: str,
    file_path: Path,
    s3_key: str,
) -> None:
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(str(file_path), s3_bucket, s3_key)
        logger.info(f"Succeed to upload {file_path} to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        logger.info(f"Failed to upload {file_path}. Error: {e}")


def register_model_registry(table_name: str, model_name: str, version: str, metadata: dict[str, Any]) -> None:
    logger.info(f"Start register model registry: {table_name=} {model_name=}, {version=}, {metadata=}")
    client = boto3.client("dynamodb")

    serializer = TypeSerializer()
    metadata_dynamodb_type = {k: serializer.serialize(str(v)) for k, v in metadata.items()}
    logger.info(f"{metadata_dynamodb_type=}")

    try:
        client.put_item(
            TableName=table_name,
            Item={
                "model": {"S": model_name},
                "version": {"S": version},
                **metadata_dynamodb_type,
            },
        )
        logger.info("Finished register model registry.")
    except Exception as e:
        logger.info(f"Failed to register model registry. Error: {e}")


def get_latest_model_version(table: str, model: str) -> str | None:
    logger.info(f"Start getting latest version for model: {table=}, {model=}")
    client = boto3.client("dynamodb")

    try:
        response = client.query(
            TableName=table,
            KeyConditionExpression="model = :model",
            ExpressionAttributeValues={":model": {"S": model}},
            ProjectionExpression="version",
            ScanIndexForward=False,
            Limit=1,
        )
        latest_version = response["Items"][0]["version"]["S"]
        logger.info(f"Found latest version for model {model}: {latest_version}")
        return latest_version

    except Exception as err:
        logger.info(f"Failed to get latest version for model {model}. Error: {err}")
        return None


def get_model_s3_key(table: str, model: str, version: str) -> str | None:
    logger.info(f"Start get model s3 key from dynamodb: {table=}, {model=}, {version=}")
    client = boto3.client("dynamodb")

    try:
        response = client.query(
            TableName=table,
            KeyConditionExpression="model = :model AND version = :version",
            ExpressionAttributeValues={":model": {"S": model}, ":version": {"S": version}},
            ProjectionExpression="model_s3_path",
        )
        if len(response["Items"]) == 0:
            logger.info(f"Model {model} version {version} not found in DynamoDB.")
            return None
        model_s3_path = response["Items"][0]["model_s3_path"]["S"]
        logger.info(f"Finished get model s3 key from dynamodb: {model_s3_path=}")
        return model_s3_path

    except Exception as err:
        logger.info(f"Failed to get model s3 key from dynamodb. {err}")
        return None


def put_csv_to_dynamodb(df: pd.DataFrame, table_name: str) -> None:
    logger.info(f"Start put csv to dynamodb {table_name=}, {df.shape=}")
    dynamo = boto3.resource("dynamodb")
    dynamo_table = dynamo.Table(table_name)
    with dynamo_table.batch_writer() as batch:
        for item in tqdm(df.T.to_dict().values()):
            batch.put_item(Item=item)


class OnlineFeatureStoreDynamoDB:
    def __init__(self, table: str, version: str):
        self.table = table
        self.version = version
        self.client = boto3.client("dynamodb")

    def get_impression_feature(self, user_id: int) -> dict[str, str | int]:
        if self.version == "latest":
            options = {
                "TableName": self.table,
                "KeyConditionExpression": "user_id = :user_id",
                "ExpressionAttributeValues": {":user_id": {"N": str(user_id)}},
                "ScanIndexForward": False,
                "Limit": 1,
            }
        else:
            options = {
                "TableName": self.table,
                "KeyConditionExpression": "user_id = :user_id AND version = :version",
                "ExpressionAttributeValues": {":user_id": {"N": str(user_id)}, ":version": {"N": str(self.version)}},
            }

        record = {}
        try:
            response = self.client.query(**options)
            if response["Items"]:
                logger.info(f"{response=}")
                item = response["Items"][0]
                logger.info(f"{item=}")
                for key, value_type in item.items():
                    if "N" in value_type:
                        value = value_type["N"]
                    elif "S" in value_type:
                        value = value_type["S"]
                    else:
                        value = np.nan
                    record[key] = value
            logger.info(f"{record=}")
            return record

        except Exception as e:
            logger.info(f"Error: {e}")
            return record


def run_task(command: list[str], cpu: int = 1024, memory: int = 2048) -> None:
    command = ["python"] + command
    command.remove("--ecs")

    ecs_client = boto3.client("ecs")
    response = ecs_client.run_task(
        cluster="mlops-ecs",
        taskDefinition="train-experiment",
        launchType="FARGATE",
        platformVersion="LATEST",
        networkConfiguration={
            "awsvpcConfiguration": {
                "subnets": [PUBLIC_SUBNET_1A],
                "securityGroups": [TRAIN_SECURITY_GROUP],
                "assignPublicIp": "DISABLED",
            }
        },
        overrides={
            "cpu": str(cpu),
            "memory": str(memory),
            "containerOverrides": [
                {
                    "name": "train",
                    "cpu": cpu,
                    "memory": memory,
                    "command": command,
                }
            ],
        },
    )

    cluster_name = response["tasks"][0]["clusterArn"].split("/")[-1]
    task_id = response["tasks"][0]["taskArn"].split("/")[-1]
    print(f"https://ap-northeast-1.console.aws.amazon.com/ecs/v2/clusters/{cluster_name}/tasks/{task_id}")
