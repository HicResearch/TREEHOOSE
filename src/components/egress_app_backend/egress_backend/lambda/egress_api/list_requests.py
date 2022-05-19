# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import os

import boto3
from aws_lambda_powertools import Logger, Tracer

tracer = Tracer(service="ListRequestsAPI")
logger = Logger(service="ListRequestsAPI")

ddb = boto3.resource("dynamodb")
table = os.environ["TABLE"]


def list_requests():
    logger.debug("List Requests API invoked")

    ddb_table = ddb.Table(table)

    response = ddb_table.scan()

    logger.debug("Succesful database scan of all egress requests")
    return response["Items"]
