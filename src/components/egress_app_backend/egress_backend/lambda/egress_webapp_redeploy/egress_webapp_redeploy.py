# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import os

import boto3
from aws_lambda_powertools import Logger

logger = Logger(service="EgressWebappRedeploy", sample_rate=0.1)

amplifycl = boto3.client("amplify")

egress_webapp_bucket_name = os.environ.get("EGRESS_WEBAPP_BUCKET_NAME")
egress_webapp_id = os.environ.get("EGRESS_WEBAPP_ID")
egress_webapp_branch = os.environ.get("EGRESS_WEBAPP_BRANCH")


@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    logger.info("Starting redeployment of the egress web app in Amplify")

    logger.debug("Egress webapp bucket name: " + egress_webapp_bucket_name)

    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    object_key = event["Records"][0]["s3"]["object"]["key"]

    # safety check
    if bucket_name == egress_webapp_bucket_name and object_key == "build.zip":
        amplifycl.start_deployment(
            appId=egress_webapp_id,
            branchName=egress_webapp_branch,
            sourceUrl=f"s3://{bucket_name}/{object_key}",
        )

    return True
