# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import os

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

tracer = Tracer(service="HandleEgressRejection")
logger = Logger(service="HandleEgressRejection", sample_rate=0.1)
metrics = Metrics(service="HandleEgressRejection", namespace="EgressRequests")
s3 = boto3.client("s3")

egress_staging_bucket = os.environ.get("EGRESS_STAGING_BUCKET")


@metrics.log_metrics()
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    workspace_id = event["workspace_id"]

    egress_request_id = event["egress_request_id"]

    logger.info("Rejecting request with egress request ID: " + egress_request_id)
    logger.debug("Staging bucket: " + egress_staging_bucket)

    response = delete_staged_objects(
        source_bucket=egress_staging_bucket,
        workspace_id=workspace_id,
        egress_request_id=egress_request_id,
    )
    if response:
        metrics.add_metric(name="EgressRequestRejected", value=1, unit=MetricUnit.Count)
    return response


def delete_staged_objects(
    source_bucket: str, workspace_id: str, egress_request_id: str
):
    object_list = []
    get_objects_list(source_bucket, workspace_id, object_list, egress_request_id)
    if object_list:
        return delete_objects(object_list, source_bucket)
    else:
        logger.warn("No objects were found in the source bucket")
        return False


####################################################################
# get_object_list
# retrieves objects from bucket with specified prefix
####################################################################
def get_objects_list(bucket, workspace_id, object_list, egress_request_id):
    """
    :param bucket: source bucket
    :type bucket: string
    :param workspace_id: workspace id
    :type id: string
    :param object_list: list of objects
    :type object_list: []
    :param egress_request_id: egress request id
    :type id: string
    :return: []
    """
    # prepare args for retrieving items from a prefix (items from a certain prefix only)
    kwargs = {"Bucket": bucket, "Prefix": f"{workspace_id}/{egress_request_id}"}

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(**kwargs)

    for page in pages:
        for obj in page["Contents"]:
            object_k = obj["Key"]
            if object_k.endswith("/"):
                # this is not an object
                continue
            else:
                object_list.append(object_k)

    logger.info("Retrieved list of objects")
    logger.debug("Object list: ", object_list)
    return object_list


##########################################################################################################
# delete_objects
# deletes rejected egress objects from the staging bucket
##########################################################################################################
def delete_objects(object_list, source_bucket):
    """
    :param object_list: list of objects to delete
    :type object_list: []

    :param source_bucket: S3 bucket containing the egress objects
    :type source_bucket: string

    :return: bool
    """
    # retrieve objects in the list
    for _counter, obj in enumerate(object_list, start=1):
        # create arguments for delete object call in staging bucket
        kwargs = {"Bucket": source_bucket, "Key": obj}

        # delete objects in staging bucket
        s3.delete_object(**kwargs)
        logger.debug("Deleted %s from %s", str(obj), source_bucket)

    logger.info("Deleted %s object(s) from staging bucket", str(_counter))
    return True
