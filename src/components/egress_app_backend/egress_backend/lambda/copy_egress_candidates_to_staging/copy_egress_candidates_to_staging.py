# (c) 2022 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
# This AWS Content is provided subject to the terms of the AWS Customer
# Agreement available at https://aws.amazon.com/agreement or other written
# agreement between Customer and Amazon Web Services, Inc.

import json
import os

import boto3
from aws_lambda_powertools import Logger, Metrics, Tracer
from aws_lambda_powertools.metrics import MetricUnit

tracer = Tracer(service="EgressCopyToStaging")
logger = Logger(service="EgressCopyToStaging", sample_rate=0.1)
metrics = Metrics(service="EgressCopyToStaging", namespace="EgressRequests")
s3 = boto3.client("s3")

target_bucket = os.environ.get("EGRESS_STAGING_BUCKET")
notification_bucket = os.environ.get("NOTIFICATION_BUCKET")


@metrics.log_metrics()
@tracer.capture_lambda_handler
@logger.inject_lambda_context(log_event=True)
def handler(event, context):
    s3_egress_store_bucket = event["s3_bucketname"]
    workspace_id = event["workspace_id"]
    egress_request_id = event["egress_request_id"]
    ver_object_list_location = event["egress_store_object_list_location"]

    logger.info(
        "Starting copy to staging bucket with egress request ID: " + egress_request_id
    )

    logger.debug("Egress Store Bucket: " + s3_egress_store_bucket)
    logger.debug("Staging bucket: " + target_bucket)
    logger.debug("Version metadata file location: " + ver_object_list_location)

    ver_object_list = fetch_object_version(ver_object_list_location)

    copy_files_to_egress_staging(
        version_list=ver_object_list,
        source_bucket=s3_egress_store_bucket,
        workspace=workspace_id,
        egress_request_id=egress_request_id,
    )
    metrics.add_metric(name="EgressRequestStaged", value=1, unit=MetricUnit.Count)

    return {
        "file_extensions": list(
            extension_set
        ),  # convert set to list which is easily serializable into JSON
        "staged": True,
    }


def fetch_object_version(version_metadata_location: str):
    file_key = version_metadata_location.split("/", 1)[1]

    # Fetch S3 object containing json list of object versions
    data = s3.get_object(Bucket=notification_bucket, Key=file_key)
    json_data = data["Body"].read().decode("utf-8")

    logger.info("Succesfully fetched versions metadata file")
    return json.loads(json_data)


def copy_files_to_egress_staging(
    version_list: object, source_bucket: str, workspace: str, egress_request_id: str
):
    object_list = []
    get_objects_list(source_bucket, workspace, object_list)
    if object_list:
        copy_objects(
            version_list,
            object_list,
            target_bucket,
            source_bucket,
            workspace,
            egress_request_id,
        )
    else:
        logger.warn("No objects were found in the source bucket")


####################################################################
# get_object_list
# retrieves objects from bucket with specified prefix
####################################################################
def get_objects_list(bucket, prefix, object_list):
    """
    :param bucket: source bucket
    :type bucket: string
    :param prefix: s3 workspace prefix
    :type prefix: string
    :param object_list: list of objects
    :type object_list: []
    :return: []
    """
    # prepare args for retrieving items from a prefix (items from a certain prefix only)
    kwargs = {"Bucket": bucket, "Prefix": prefix}

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


####################################################################
# copy_objects
# copies candidate egress objects to staging bucket
####################################################################
def copy_objects(
    version_list: object,
    object_list: str,
    target_bucket: str,
    source_bucket: str,
    workspace_id: str,
    egress_request_id: str,
):
    """
    :param object_list: list of S3 objects
    :type bucket: []
    :param target_bucket: location to copy objects to
    :type prefix: string
    :param source_bucket: source S3 bucket
    :type : string
    :param workspace_id: Workspace ID
    :type : string
    :param egress_request_id: Egress request ID which will form part of the object key
    :type : string
    :return: bool
    """

    # Define global variable to hold set of unique extensions
    global extension_set
    extension_set = set()

    # Retrieve object from object list
    for _counter, obj in enumerate(object_list, start=1):
        # split the object key into parts
        obj_parts = split_object_key(obj)
        file_name = obj_parts[-1]

        # Retrieve the right object metadata from version list
        versioned_object = next(
            object_k for object_k in version_list["objects"] if object_k["Key"] == obj
        )

        # retrieve version attribute
        object_version_id = versioned_object["VersionId"]

        # create arguments for copy object call
        kwargs = {
            "Bucket": target_bucket,
            "CopySource": f"{source_bucket}/{obj}?versionId={object_version_id}",
            "Key": f"{workspace_id}/{egress_request_id}/{file_name}",
        }

        # copy objects to destination bucket
        s3.copy_object(**kwargs)
        logger.debug(
            "Copied %s with %s from %s to %s",
            str(obj),
            str(object_version_id),
            source_bucket,
            target_bucket,
        )

        extension_set.add(get_file_extension(file_name))

    logger.info("Copied %s versioned object/s to staging bucket", str(_counter))
    return True


def split_object_key(path: str):
    return path.split("/")


def get_file_extension(path: str):
    split = path.split(".")
    if len(split) > 1:
        return split[-1]
    else:
        return ""
