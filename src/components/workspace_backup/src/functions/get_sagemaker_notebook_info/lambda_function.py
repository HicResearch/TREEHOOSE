# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import json
import os

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from botocore.config import Config

tracer = Tracer(service="TREGetSagemakerNotebookInfoFunction")
logger = Logger(service="TREGetSagemakerNotebookInfoFunction", sample_rate=0.1)
metrics = Metrics(
    service="TREGetSagemakerNotebookInfoFunction",
    namespace="TREBackups",
)

sagemaker = boto3.client("sagemaker")
iam_client = boto3.client("iam")
s3_client = boto3.client("s3", config=Config(signature_version="s3v4"))

BACKUP_TAG = json.loads(os.environ["BACKUP_TAG"])
BACKUP_BUCKET = os.environ["BACKUP_BUCKET"]
ACCOUNT = os.environ["ACCOUNT"]
BACKUP_SCHEDULE = os.environ["BACKUP_SCHEDULE"]


def lambda_handler(event, context):
    logger.info(event)

    notebook_name = event["detail"]["requestParameters"]["notebookInstanceName"]
    notebook_role_arn = event["detail"]["requestParameters"]["roleArn"]
    notebook_role_name = notebook_role_arn.split("/")[1]
    notebook_tags = event["detail"]["requestParameters"]["tags"]
    notebook_backup_tag = [
        tag["value"] for tag in notebook_tags if tag["key"] == BACKUP_TAG.get("Key")
    ]
    notebook_cfn_stack_name = [
        tag["value"]
        for tag in notebook_tags
        if tag["key"] == "aws:cloudformation:stack-name"
    ][0]

    if not notebook_backup_tag:
        logger.info("backup tag not found on instance %s", notebook_name)

        return {
            "original_event": event,
            "notebook_backup_enabled": False,
        }

    s3_response = s3_client.put_object(Bucket=BACKUP_BUCKET, Key=(notebook_name + "/"))

    logger.info("Backup prefix created for notebook %s", notebook_name)
    logger.debug(s3_response)

    return {
        "notebook_backup_enabled": True,
        "notebook_name": notebook_name,
        "notebook_role_name": notebook_role_name,
        "notebook_cfn_stack_name": notebook_cfn_stack_name,
    }
