# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import os

import boto3
from aws_lambda_powertools import Logger, Tracer

tracer = Tracer(service="TriggerEgressWorkflow")
logger = Logger(service="TriggerEgressWorkflow")

ddb = boto3.client("dynamodb")
table = os.environ["TABLE"]


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    return ddb.update_item(
        TableName=table,
        Key={"egress_request_id": {"S": event["input"]}},
        UpdateExpression="set task_token=:t, current_reviewer_group=:r",
        ExpressionAttributeValues={
            ":t": {"S": event["token"]},
            ":r": {"S": event["current_reviewer_group"]},
        },
        ReturnValues="ALL_NEW",
    )
