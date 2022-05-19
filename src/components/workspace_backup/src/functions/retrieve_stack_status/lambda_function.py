# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer

tracer = Tracer(service="TRERetrieveCfnStackStatusFunction")
logger = Logger(service="TRERetrieveCfnStackStatusFunction", sample_rate=0.1)
metrics = Metrics(
    service="TRERetrieveCfnStackStatusFunction",
    namespace="TREBackups",
)
cfn_client = boto3.client("cloudformation")


def lambda_handler(event, context):
    notebook_cfn_stack_name = event["notebook_cfn_stack_name"]

    stack_response = cfn_client.describe_stacks(
        StackName=notebook_cfn_stack_name,
    )

    logger.debug(stack_response)

    event["stack_status"] = stack_response["Stacks"][0]["StackStatus"]
    logger.info(
        "Stack status for notebook %s is %s",
        event["notebook_name"],
        event["stack_status"],
    )
    return event
