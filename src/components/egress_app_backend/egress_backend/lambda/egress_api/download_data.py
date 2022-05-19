# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import os
from typing import Any

import boto3
from aws_lambda_powertools import Logger, Tracer
from botocore.config import Config
from botocore.exceptions import ClientError

tracer = Tracer(service="DownloadDataAPI")
logger = Logger(service="DownloadDataAPI")
####################################################################
#
# AWS client connections
#
####################################################################
s3_client = boto3.client(
    "s3", config=Config(signature_version="s3v4"), region_name=os.environ["REGION"]
)

ddb = boto3.resource("dynamodb")
####################################################################
#
# Variable assignments
#
####################################################################
bucket = os.environ["DATALAKE_BUCKET"]
table = os.environ["TABLE"]
max_downloads_allowed = os.environ["MAX_DOWNLOADS_ALLOWED"]


@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def download_data(arguments: str, context: Any):

    try:
        # Static filename
        file = "egress_data.zip"
        top_level_prefix = "approved_egress"

        # Get the relevant fields from the request
        inbound_egress_request_id = arguments["request"]["egress_request_id"]
        inbound_workspace_id = arguments["request"]["workspace_id"]
        inbound_download_count = arguments["request"]["download_count"]

        logger.info(
            "Download Data API invoked with Egress Request ID: %s",
            inbound_egress_request_id,
        )

        # If downloads are allowed
        if int(inbound_download_count) < int(max_downloads_allowed):

            # Construct object key from request fields
            object_key = f"{top_level_prefix}/{inbound_workspace_id}/{inbound_egress_request_id}/{file}"

            # Check if file exists in bucket
            head_obj_response = s3_client.head_object(Bucket=bucket, Key=object_key)
            logger.debug("HEAD OBJECT RESPONSE: " + str(head_obj_response))

            # Generate presign URL
            presign = s3_client.generate_presigned_url(
                "get_object",
                ExpiresIn=3600,
                Params={"Bucket": bucket, "Key": object_key},
            )
            logger.debug("Presign URL generated: %s", presign)

            # Update count field in DB
            update_count_in_db(
                inbound_egress_request_id, int(inbound_download_count) + 1
            )

            # Return URL
            logger.info("Presign URL generated")
            return {"presign_url": presign}

        # If data has been downloaded before
        else:
            response = "Download limit exceeded. Please contact an administrator"
            logger.warn(response)
    except ClientError as e:
        response = "Error from lambda_handler: " + e.response["Error"]["Message"]
        logger.error(e.response["Error"]["Message"])


def update_count_in_db(request_id, inbound_count):
    # Initialise dynamodb table connection
    ddb_table = ddb.Table(table)

    # Set download_count field to 1
    ddb_table.update_item(
        Key={"egress_request_id": request_id},
        UpdateExpression="SET download_count = :count",
        ExpressionAttributeValues={":count": inbound_count},
    )
